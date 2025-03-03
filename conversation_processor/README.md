# Conversation Processor (Redshift)

## Description
This project processes **conversation data** and uploads it into **Amazon Redshift** for further analysis.
It retrieves data from an **external source** (like the Amelia API or any other system), performs necessary transformations, and then loads the cleaned data into a **Redshift table**.
This system can be integrated into a data pipeline to automate the storage and analysis of conversation data.

### Key Features:
- **Data Extraction**: Retrieves raw conversation data from an external source (e.g., Amelia API or other systems).
- **Data Processing**: Cleans and formats the data, including handling timestamps and custom metrics.
- **Redshift Integration**: Uploads the processed data into **Amazon Redshift** for storage and analysis.
- **Timestamp Conversion**: Converts ISO 8601 timestamps to a Redshift-compatible format.
- **Custom Metrics Parsing**: Parses and formats custom metrics associated with each conversation.

### Workflow:
1. **Data Extraction**: Data is fetched from an external source like the Amelia API (or any other source).
2. **Data Processing**:
   - The data undergoes necessary transformations, including timestamp conversion and parsing of custom metrics.
   - The conversation data is structured and cleaned.
3. **Data Upload**: The processed data is uploaded into a **Redshift table** for further analysis and reporting.
4. **Redshift Table**: The data is inserted into a Redshift table for easy querying.

### Main Components:
- **AWS Lambda**: Automates the entire data processing and upload workflow.
- **Amazon Redshift**: Stores the processed conversation data.
- **Amazon S3** (optional): Can be used to store intermediate files if needed.

## Environment Variables:
The following environment variables must be set in AWS Lambda for the function to work:
- **`REDSHIFT_WORKGROUP_NAME`**: The Redshift workgroup name.
- **`REDSHIFT_DATABASE`**: The name of the Redshift database.
- **`S3_BUCKET_NAME`**: The name of the S3 bucket where raw data is stored (if used).
- **`S3_FILE_KEY`**: The key (path) of the file in S3 (if used).

