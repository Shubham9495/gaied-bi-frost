from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
from typing import List, Optional
import json
import os

app = FastAPI()

RULES_FILE = "rules.json"  # Path to the JSON file that stores rules

# Function to load the rules from the JSON file
def load_rules():
    if os.path.exists(RULES_FILE):
        with open(RULES_FILE, "r") as file:
            return json.load(file)
    else:
        return {}

# Function to save the rules to the JSON file
def save_rules(rules_db):
    with open(RULES_FILE, "w") as file:
        json.dump(rules_db, file, indent=4)

# In-memory storage of rules (initially empty)
rules_db = load_rules()

# Pydantic model to represent the rule request
class SubRequest(BaseModel):
    name: str
    keywords: List[str]

    @validator('keywords')
    def check_keywords(cls, v):
        if not v:
            raise ValueError('Keywords cannot be empty.')
        if any(not isinstance(keyword, str) or not keyword.strip() for keyword in v):
            raise ValueError('Each keyword must be a non-empty string.')
        return v

class Rule(BaseModel):
    request_type: str
    sub_request_types: List[SubRequest]

@app.get("/rules")
def get_rules():
    return rules_db

@app.post("/rules")
def add_rule(rule: Rule):
    # Check if category already exists
    if rule.request_type in rules_db:
        raise HTTPException(status_code=400, detail="Category already exists")

    # Process sub_request_types and add them to the rule
    rules_db[rule.request_type] = [
        {"name": sub_request.name, "keywords": sub_request.keywords}
        for sub_request in rule.sub_request_types
    ]
    save_rules(rules_db)  # Save the updated rules to the file
    return {"message": "Rule added successfully"}

@app.put("/rules/{category}")
def update_rule(category: str, rule: Rule):
    # Check if the category exists
    if category not in rules_db:
        raise HTTPException(status_code=404, detail="Category not found")

    # Update the rule for the category
    rules_db[category] = [
        {"name": sub_request.name, "keywords": sub_request.keywords}
        for sub_request in rule.sub_request_types
    ]
    save_rules(rules_db)  # Save the updated rules to the file
    return {"message": f"Rule for '{category}' updated successfully"}

@app.delete("/rules/{category}")
def delete_rule(category: str):
    # Check if the category exists
    if category not in rules_db:
        raise HTTPException(status_code=404, detail="Category not found")

    # Delete the rule for the category
    del rules_db[category]
    save_rules(rules_db)  # Save the updated rules to the file
    return {"message": f"Rule for '{category}' deleted successfully"}
