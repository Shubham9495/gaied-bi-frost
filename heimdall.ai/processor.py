import ollama
import json
import os

# Path to the JSON file that stores rules
RULES_FILE = "rules.json"

# Function to load the rules from the JSON file
def load_rules():
    if os.path.exists(RULES_FILE):
        with open(RULES_FILE, "r") as file:
            return json.load(file)
    else:
        return {}

# Function to generate the prompt dynamically based on the loaded rules
def generate_prompt(subject, email_content, rules_db):
    # Combine the subject and email content
    combined_content = f"Subject: {subject}\n\nContent: {email_content}"

    # Start building the prompt
    prompt = f"Classify the intent of the following email into predefined categories:\n"

    # Loop through each category in the rules and add it to the prompt
    for category in rules_db.get("categories", []):
        request_type = category.get("request_type", "Unknown")
        prompt += f" - '{request_type}': "

        # Loop through each sub_request_type and its associated keywords
        for sub_request in category.get("sub_request_types", []):
            sub_request_name = sub_request.get("name", "Unknown")
            keywords = ", ".join(sub_request.get("keywords", []))
            prompt += f"{sub_request_name} (keywords: {keywords}), "

        # Trim any extra comma and space
        prompt = prompt.rstrip(", ")  # Remove last comma and space
        prompt += ".\n"

    # Add additional instructions
    prompt += (
        "If the email matches none of the above categories, classify it as 'No intent identified'.\n"
        "Provide a confidence score for the classification. Make sure The response is always in following JSON format which should adhere with the rules mentioned above: "
        "{'request_type': 'value', 'sub_request_type': 'value', 'confidence_score': 'value'}\n\n"
        f"{combined_content}"
    )

    return prompt

def process_email(subject, email_content):
    # Load rules from the JSON file
    rules_db = load_rules()

    if not rules_db.get("categories"):
        return {"error": "No categories found in rules database."}

    # Generate the dynamic prompt based on the loaded rules
    prompt = generate_prompt(subject, email_content, rules_db)

    # Make the call to the Llama model
    response = ollama.chat(model="llama3.2:3b", messages=[{"role": "user", "content": prompt}])

    # Check if the response contains the expected content
    try:
        # Extract the content of the message from the response
        content = response['message']['content']
        print(content)

        # Parse the JSON response
        parsed_response = json.loads(content)  # Safely convert the string to a dictionary

        # Extract the values
        request_type = parsed_response.get('request_type', "No request type found")
        sub_request_type = parsed_response.get('sub_request_type', "No sub-request type found")
        confidence = parsed_response.get('confidence_score', "No confidence score found")

        # Return the classification and confidence score
        return {
            "request_type": request_type,
            "sub_request_type": sub_request_type,
            "confidence_score": confidence
        }
    except (KeyError, json.JSONDecodeError):
        # Handle cases where the response doesn't contain the expected content or is not valid JSON
        return {"error": "Error: Unable to extract message content from response."}
