import requests
import json
import boto3
import datetime

# AWS S3 client
s3 = boto3.client('s3')

# Define a fixed S3 bucket name (replace with your actual bucket name)
S3_BUCKET_NAME = "conversation-exports"

def get_token(username, password):
    """Authenticate and retrieve token"""
    url = "https://mskcc.demo.amelia.com/AmeliaRest/api/v1/auth/login"
    payload = json.dumps({"username": username, "password": password})
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=payload)

    if response.status_code == 201:
        return response.json().get('token')
    else:
        raise Exception(f"Failed to retrieve token: {response.text}")

def get_domains(token):
    """Retrieve available domains"""
    url = "https://mskcc.demo.amelia.com/AmeliaRest/api/v1/admin/domains/"
    headers = {'X-Amelia-Rest-Token': token}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json().get('content', [])
    else:
        raise Exception(f"Failed to retrieve domains: {response.text}")

def fetch_conversation_export(token, domain_id, from_date, to_date):
    """Fetch export and save to a single S3 bucket with unique filenames"""
    
    # Generate a unique filename using timestamp
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = f"conversation_export_{domain_id}_{timestamp}.csv"

    url = "https://mskcc.demo.amelia.com/AmeliaRest/api/v1/admin/metrics/domains/conversations/export"
    params = {
        "domainIds": domain_id,
        "from": from_date,
        "to": to_date,
        "format": "csv"
    }
    headers = {'X-Amelia-Rest-Token': token}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        # Upload the CSV file to a fixed S3 bucket with a unique name
        s3.put_object(Bucket=S3_BUCKET_NAME, Key=output_file, Body=response.content)
        print(f"CSV file uploaded to S3 bucket '{S3_BUCKET_NAME}' as '{output_file}'")
        return {"status": "Success", "file": output_file, "bucket": S3_BUCKET_NAME}
    else:
        raise Exception(f"Failed to fetch the export: {response.text}")

def lambda_handler(event, context):
    """AWS Lambda entry point"""
    username = event.get('username')
    password = event.get('password')
    domain_choice = event.get('domain_choice')
    from_date = event.get('from_date')
    to_date = event.get('to_date')

    if not all([username, password, domain_choice, from_date, to_date]):
        return {"status": "Error", "message": "Missing required parameters."}

    try:
        token = get_token(username, password)
        domains = get_domains(token)

        # Find selected domain
        domain = next((d for d in domains if d['name'] == domain_choice), None)
        if not domain:
            return {"status": "Error", "message": f"Domain '{domain_choice}' not found."}

        # Fetch and save the export in the fixed S3 bucket
        result = fetch_conversation_export(token, domain['id'], from_date, to_date)
        return result

    except Exception as e:
        return {"status": "Error", "message": str(e)}
