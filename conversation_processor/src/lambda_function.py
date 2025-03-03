import boto3
import pandas as pd
import json
import os
import time
import io
from datetime import datetime

# AWS Configuration
AWS_REGION = "us-east-1"

# Load Redshift and S3 credentials from environment variables
REDSHIFT_WORKGROUP_NAME = os.environ['REDSHIFT_WORKGROUP_NAME']
REDSHIFT_DATABASE = os.environ['REDSHIFT_DB']
S3_BUCKET_NAME = os.environ['S3_BUCKET_NAME']
S3_FILE_KEY = os.environ['S3_FILE_KEY']

# Create AWS clients
s3 = boto3.client("s3")
redshift_data = boto3.client("redshift-data", region_name=AWS_REGION)

def convert_timestamp(timestamp_str):
    """Converts ISO 8601 timestamp to Redshift-compatible format."""
    try:
        if pd.isna(timestamp_str) or not timestamp_str:
            return None  # Return None if the timestamp is empty
        
        # Remove [UTC] if present
        timestamp_str = timestamp_str.replace("[UTC]", "").replace("Z", "")

        # Convert to Redshift-compatible format (YYYY-MM-DD HH:MI:SS)
        dt = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%f")  # Handles milliseconds
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print(f"Error converting timestamp: {timestamp_str}, Error: {e}")
        return None  # Return None if conversion fails
        
def parse_custom_metrics(custom_metrics):
    """Parses custom metrics from raw data and returns a dictionary."""
    parsed_data = {}
    if not custom_metrics:
        return parsed_data  # Return empty dictionary if no data

    key_values = custom_metrics.split("||")  # Split by ||
    for key_value in key_values:
        try:
            key, value = key_value.split("=", 1)  # Split by the first =
            parsed_data[key.strip()] = value.strip()  # Store key-value pairs
        except ValueError:
            print(f"Error parsing custom metric: {key_value}")

    return parsed_data  # Return dictionary

def parse_transcript(transcript):
    """Parses transcript data into structured format."""
    conversations = []
    
    if pd.isna(transcript) or not isinstance(transcript, str):
        return json.dumps(conversations)

    transcript_entries = transcript.split("||")
    
    for entry in transcript_entries:
        try:
            speaker, content = entry.split("]:")
            speaker = speaker.replace("[", "").strip()
            conversations.append({"Speaker": speaker, "Message": content.strip()})
        except Exception as e:
            print(f"Error parsing transcript entry: {entry}")
    
    return json.dumps(conversations)

def escape_quotes(value):
    """Escapes single quotes in text values to prevent SQL errors."""
    if isinstance(value, str):
        return value.replace("'", "''")  # Replace ' with ''
    return value

def execute_query(query):
    """Executes an SQL query on Amazon Redshift using the Data API."""
    response = redshift_data.execute_statement(
        WorkgroupName=REDSHIFT_WORKGROUP_NAME,
        Database=REDSHIFT_DATABASE,
        Sql=query
    )
    return response["Id"]

def check_query_status(query_id):
    """Checks the status of the executed query."""
    while True:
        response = redshift_data.describe_statement(Id=query_id)
        if response["Status"] in ["FAILED", "FINISHED"]:
            return response
        time.sleep(2)

def upload_to_redshift(df):
    """Uploads the cleaned DataFrame to Redshift."""
    for _, row in df.iterrows():
        insert_query = f"""
        INSERT INTO conversations (
            conversation_id, datetime, channel, transcript, 
            call_id, escalation_reason, intent, agent_picked_up, aiops_ticket, 
            contact_id, conversation_started, initial_user_utterance, 
            second_intent, third_intent, pre_close_started, first_intent, containment,
            web_option, exception_in_preclose, call_escalated, intent_history,
            closed_by, third_user_utterance, second_user_utterance
        ) VALUES (
            '{escape_quotes(row["Conversation Id"])}',
            {f"'{row['DateTime']}'" if pd.notna(row['DateTime']) else 'NULL'},  -- Handle NULL timestamps
            '{escape_quotes(row["Channel"])}',
            '{escape_quotes(row["Transcript"])}',
            '{escape_quotes(row["Call ID"])}',
            '{escape_quotes(row["Escalation Reason"])}',
            '{escape_quotes(row["Intent"])}',
            {row["Agent Picked Up"]},  
            '{escape_quotes(row["AIOPS Ticket"])}',
            '{escape_quotes(row["Contact ID"])}',
            {row["Conversation Started"]},  
            '{escape_quotes(row["Initial User Utterance"])}',
            '{escape_quotes(row["Second Intent"])}',
            '{escape_quotes(row["Third Intent"])}',
            {row["Pre Close Started"]},  
            '{escape_quotes(row["First Intent"])}',
            {row["Containment"]},  -- BOOLEAN
            '{escape_quotes(row["WebOption"])}',
            {row["ExceptionInPreClose"]},  -- BOOLEAN
            {row["CallEscalated"]},  -- BOOLEAN
            '{escape_quotes(row["IntentHistory"])}',
            '{escape_quotes(row["ClosedBy"])}',
            '{escape_quotes(row["ThirdUserUtterance"])}',
            '{escape_quotes(row["SecondUserUtterance"])}'
        );
        """
        query_id = execute_query(insert_query)
        status = check_query_status(query_id)
        if status["Status"] == "FAILED":
            print(f"Error inserting row: {status['Error']}")

def lambda_handler(event, context):
    """AWS Lambda entry point: Retrieves data from S3, cleans it, and uploads to Redshift."""

    # Retrieve file from S3
    response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=S3_FILE_KEY)
    data = response['Body'].read().decode('utf-8')

    # Convert CSV data into DataFrame
    row_data = pd.read_csv(io.StringIO(data))

    # Process and clean the data
    cleaned_data = []
    for _, row in row_data.iterrows():
        custom_metrics_json = parse_custom_metrics(row["Custom Metrics"])
        raw_data = {
            "Conversation Id": escape_quotes(row["Conversation Id"]),
        "DateTime": convert_timestamp(row["Created"]),  # Convert timestamp here
        "Channel": escape_quotes(row["Channel"]),
        "Custom Metrics": escape_quotes(json.dumps(custom_metrics_json)),
        "Transcript": escape_quotes(parse_transcript(row["Transcript"])),
        "Call ID": escape_quotes(custom_metrics_json.get("CallID", "")),
        "Escalation Reason": escape_quotes(custom_metrics_json.get("EscalationReason", "")),
        "Intent": escape_quotes(custom_metrics_json.get("Intent", "")),
        "Agent Picked Up": custom_metrics_json.get("Agent picked up", "False") == "True",  # Boolean conversion
        "AIOPS Ticket": escape_quotes(custom_metrics_json.get("AIOPS Ticket", "")),
        "Contact ID": escape_quotes(custom_metrics_json.get("ContactID", "")),
        "Conversation Started": custom_metrics_json.get("Conversation Started", "False") == "True",  # Boolean
        "Initial User Utterance": escape_quotes(custom_metrics_json.get("InitialUserUtterance", "")),
        "Second Intent": escape_quotes(custom_metrics_json.get("SecondIntent", "")),
        "Third Intent": escape_quotes(custom_metrics_json.get("ThirdIntent", "")),
        "Pre Close Started": custom_metrics_json.get("PreCloseStarted", "False") == "True",  # Boolean
        "First Intent": escape_quotes(custom_metrics_json.get("FirstIntent", "")),
        "Containment": custom_metrics_json.get("Containment", "False") == "True",  # Boolean
        "WebOption": escape_quotes(custom_metrics_json.get("WebOption", "")),
        "ExceptionInPreClose": custom_metrics_json.get("ExceptionInPreClose", "False") == "True",  # Boolean
        "CallEscalated": custom_metrics_json.get("CallEscalated", "False") == "True",  # Boolean
        "IntentHistory": escape_quotes(custom_metrics_json.get("intentHistory", "")),
        "ClosedBy": escape_quotes(custom_metrics_json.get("closed_by", "")),
        "ThirdUserUtterance": escape_quotes(custom_metrics_json.get("ThirdUserUtterance", "")),
        "SecondUserUtterance": escape_quotes(custom_metrics_json.get("SecondUserUtterance", ""))
    }
        cleaned_data.append(raw_data)

    # Convert cleaned data into a DataFrame
    cleaned_df = pd.DataFrame(cleaned_data)

    # Upload cleaned data to Redshift
    upload_to_redshift(cleaned_df)

    return {"statusCode": 200, "body": "Data cleaned and uploaded successfully"}