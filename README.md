# Intent Prediction Comparison Using AWS Bedrock

## Description
This project aims to **compare the intent predictions** made by **NLU models** with predictions from **AWS Bedrock**, a **Large Language Model (LLM)**. The project involves providing a set of **intents** and their associated **example utterances** to AWS Bedrock and evaluating its ability to correctly predict the intent for a new, unseen utterance.

### Key Objective:
- **Comparison of Predictions**: We compare the **intent classification** results from an **NLU model** (used by Amelia, a conversation AI tool) with those predicted by **AWS Bedrock**.
- **Intent Prediction with Bedrock**: This part of the project sends **intents and example utterances** to **AWS Bedrock** for each new **user utterance** added to **Amelia**, and checks how accurately Bedrock can classify the intent.
  
The function is triggered each time a new user utterance is added to **Amelia**, which is an **NLU-based conversation AI tool**. The goal is to analyze how **AWS Bedrock** performs in intent classification compared to the existing NLU predictions.

### How It Works:
1. **NLU Model (Amelia)** receives user input (an utterance).
2. The system **sends intent examples** (with their labels) to **AWS Bedrock** to classify the intent of the user’s utterance.
3. **Comparison of Results**: The predicted intent from **Bedrock** is compared with the **NLU model’s prediction** to evaluate how well Bedrock performs in classifying intents.

### Main Components:
- **AWS Lambda**: The function that processes incoming user utterances, sends them to AWS Bedrock for prediction, and returns the result.
- **AWS Bedrock**: The LLM used for generating intent predictions based on provided examples.
- **Amelia (NLU)**: The existing **NLU-based conversation AI tool** that provides the initial intent classification for comparison.
- **S3 Bucket**: Stores the CSV file with **intent names** and **example utterances**.

## Environment Variables:
- **`AWS_BEDROCK_MODEL_ID`**: Model ID for the Bedrock LLM used for intent classification.
- **`S3_BUCKET_NAME`**: The name of the S3 bucket where the intent examples (CSV) are stored.
- **`S3_CSV_KEY`**: Path to the CSV file containing the intents and examples.
  
