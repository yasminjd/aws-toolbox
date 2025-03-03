# AWS Conversation Exporter

## Description
This project allows for the **exporting of conversations** from a **domain** using the **Amelia API** and then **storing** the exported data in an **AWS S3 bucket**. The project utilizes **AWS Lambda** to fetch data from the Amelia REST API, authenticate the user, retrieve available domains, and export the conversation data as CSV files.

### Key Features:
- **Authentication**: Authenticates using a **username** and **password** to retrieve a **token** for accessing the API.
- **Domain Selection**: Retrieves available **domains** and selects the one specified by the user.
- **Conversation Export**: Fetches **conversation data** based on the selected domain and specified date range, and uploads the data to **AWS S3**.
- **Lambda Function**: The project is designed to run on AWS Lambda, which automatically processes the conversation export when triggered.

### Workflow:
1. **User Authentication**: The user provides a username and password to authenticate and retrieve a token.
2. **Domain Selection**: The system retrieves available domains and selects the one specified by the user.
3. **Conversation Export**: The system fetches the conversation export for the selected domain and specified date range.
4. **Data Upload**: The conversation data is uploaded to an **AWS S3 bucket** in CSV format.

### Main Components:
- **AWS Lambda**: For processing and interacting with the Amelia API.
- **AWS S3**: To store the exported CSV file.
- **Amelia API**: Used to retrieve conversation data from the selected domain.

## Environment Variables:
- **`S3_BUCKET_NAME`**: The name of the S3 bucket where the conversation export will be uploaded.
  
