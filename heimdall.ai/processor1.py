import ollama
import re
import json

def process_email(subject, email_content):
    # Combine the subject and email content
    combined_content = f"Subject: {subject}\n\nContent: {email_content}"
    
    # Use an f-string to format the prompt correctly
    prompt = f"Classify the intent of the following email into predefined categories: " \
             f" - 'Password management': keywords include 'password', 'reset', 'login', 'credentials'. " \
             f" - 'Account access': keywords include 'account', 'log in', 'access', 'signin'. " \
             f" - 'Support Request': keywords include 'help', 'assist', 'support', 'issue'. " \
             f" - 'Loan Request': keywords include 'loan', 'payment', 'request', 'due date'. " \
             f" If the email matches none of the above categories, classify it as No intent identified. " \
             f" Provide a confidence score for the classification. The response should be in JSON format: " \
             f"{{'classification': 'value', 'confidence_score': 'value'}}\n\n{combined_content}"

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
        classification = parsed_response.get('classification', "No classification found")
        confidence = parsed_response.get('confidence_score', "No confidence score found")
        
        # Return the classification and confidence score
        return {"classification": classification, "confidence_score": confidence}
    except (KeyError, json.JSONDecodeError):
        # Handle cases where the response doesn't contain the expected content or is not valid JSON
        return "Error: Unable to extract message content from response."

