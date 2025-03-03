# AWS Intent Classifier with Bedrock

## Description
This project compares the predictions of an **NLU model** (used by **Amelia**, a conversation AI tool) with those made by **AWS Bedrock**, a **Large Language Model (LLM)**, for intent classification. The Lambda function is invoked each time a new **user utterance** is added to **Amelia**, and the code processes the utterance to classify its intent using AWS Bedrock.

### Key Functionality:
1. **Loading Intents from S3**:
   - The project retrieves a list of **intents** and **example utterances** from a CSV file stored in **AWS S3**. The **intents** are used to compare how both the **NLU model** and **AWS Bedrock** predict the intent for a new user utterance.
  
2. **Generating a Prompt**:
   - The **Lambda function** generates a structured **prompt** that includes the intents and example utterances. This prompt is then sent to **AWS Bedrock** for classification.

3. **Sending to AWS Bedrock**:
   - The prompt containing intents and a new user utterance is sent to **AWS Bedrock** via the `invoke_model` API.
   - AWS Bedrock generates a response, and the system extracts the predicted intent from Bedrock’s output.

4. **Handling Incoming Utterances**:
   - The Lambda function is invoked every time a new **utterance** is received. It processes the utterance, generates the prompt, and compares **AWS Bedrock’s** prediction with the **NLU model’s** prediction.

### Workflow:
1. **Amelia (NLU-based AI tool)** adds a new user **utterance**.
2. The **Lambda function** is triggered by the new utterance.
3. The **Lambda function** loads the **intents** from an **S3 CSV file**.
4. A structured **prompt** is created and sent to **AWS Bedrock**.
5. **Bedrock’s prediction** is returned and compared to the existing **NLU model’s prediction**.
6. The predicted **intent** is returned.

### Key Services Used:
- **AWS Lambda**: For processing the request and invoking the model.
- **AWS Bedrock**: For generating predictions from the LLM.
- **AWS S3**: For storing intents and their corresponding example utterances.

## Environment Variables:
The following environment variables must be set in AWS Lambda for the function to work:
- **`AWS_BEDROCK_MODEL_ID`**: The ID of the Bedrock model to use for intent classification.
- **`S3_BUCKET_NAME`**: The name of the S3 bucket where the CSV file containing intents is stored.
- **`S3_CSV_KEY`**: The path to the CSV file containing intents and example utterances.

