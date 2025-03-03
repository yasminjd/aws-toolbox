import json
import os
import boto3
import csv
from io import StringIO
import re

# AWS Clients
s3_client = boto3.client("s3")
bedrock_runtime = boto3.client("bedrock-runtime")

# Environment Variables (Set these in AWS Lambda)
AWS_BEDROCK_MODEL_ID = os.getenv("AWS_BEDROCK_MODEL_ID")  
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")  
S3_CSV_KEY = os.getenv("S3_CSV_KEY")  # Example: "intents/intents.csv"

def load_intents_from_s3():
    """
    Loads intents and example utterances from a CSV file stored in S3.
    """
    if not S3_BUCKET_NAME or not S3_CSV_KEY:
        print("Error: S3_BUCKET_NAME or S3_CSV_KEY is missing.")
        return None  

    try:
        # Fetch CSV file from S3
        response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=S3_CSV_KEY)
        csv_content = response["Body"].read().decode("utf-8")

        # Read CSV content
        reader = csv.reader(StringIO(csv_content))
        intents_dict = {}

        for row in reader:
            if len(row) < 2:
                continue  # Skip invalid rows
            
            intent, utterance = row[0].strip(), row[1].strip()
            if intent not in intents_dict:
                intents_dict[intent] = []
            intents_dict[intent].append(utterance)

        return intents_dict

    except s3_client.exceptions.NoSuchKey:
        print(f"Error: CSV file '{S3_CSV_KEY}' not found in bucket '{S3_BUCKET_NAME}'.")
        return None  

    except Exception as e:
        print(f"Error loading intents from S3: {e}")
        return None  
def generate_prompt(utterance, intents_dict):
    """
    Generates a structured prompt using basic Python string operations.
    """

    prompt = "I am going to give you a list of labels (intents). Each label has two example utterances.\n\n"
    
    for intent, examples in intents_dict.items():
        prompt += f"{intent}:\n"
        prompt += f"Example one: \"{examples[0]}\"\n"
        prompt += f"Example two: \"{examples[1]}\"\n\n"

    prompt += f"Then, I will give you an utterance. Label it with an intent from the above list.\n"
    prompt += "Reply in the format: \"utterance == label\". Do not include extra information.\n\n"
    prompt += f"Utterance: \"{utterance}\""

    return prompt

def send_to_bedrock(prompt):
    """
    Sends the generated prompt to AWS Bedrock for processing.
    """
    try:
        kwargs = {
            "modelId": AWS_BEDROCK_MODEL_ID,
            "contentType": "application/json",
            "accept": "*/*",
            "body": json.dumps(
                {
                    "inputText": prompt,
                    "textGenerationConfig": {
                        "maxTokenCount": 512,
                        "stopSequences": [],
                        "temperature": 0.7,
                        "topP": 0.9
                    }
                }
            )
        }

        response = bedrock_runtime.invoke_model(**kwargs)
        response_body = json.loads(response.get('body').read())

        if "results" in response_body and len(response_body["results"]) > 0:
            raw_output = response_body["results"][0].get("outputText", "Error: No response from model.")

            # Remove unwanted characters (e.g., '\n' and "utterance ==")
            cleaned_output = raw_output.strip().replace("utterance ==", "").strip()

            return cleaned_output  # Should return only "age_limit"

        else:
            return "Error: Bedrock response format incorrect."

    except Exception as e:
        print(f"Error in Bedrock processing: {str(e)}")
        return f"Error: {str(e)}"

    except Exception as e:
        print(f"Error in Bedrock processing: {str(e)}")
        return "Bedrock fallback: Unable to process request."

def lambda_handler(event, context):
    """
    AWS Lambda entry point. Loads intents from S3, generates a prompt, and processes it through AWS Bedrock.
    """
    try:
        body = json.loads(event.get("body", "{}"))
        utterance = body.get("utterance")

        if not utterance:
            return {"statusCode": 400, "body": json.dumps({"message": "Utterance is required"})}

        # Load intents dynamically from S3
        intents_dict = load_intents_from_s3()
        if not intents_dict:
            return {"statusCode": 500, "body": json.dumps({"message": "Failed to load intents from S3"})}

        # Generate prompt
        prompt = generate_prompt(utterance, intents_dict)

        # Get labeled intent from AWS Bedrock
        labeled_intent = send_to_bedrock(prompt)

        return {
            "statusCode": 200,
            "body": json.dumps({"utterance": utterance, "intent": labeled_intent})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Internal server error", "error": str(e)})
        }