from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from processor import process_email

app = FastAPI()

class EmailRequest(BaseModel):
    subject: str
    email_content: str  # This should match the field name in the request

@app.post("/analyze-email")
def analyze_email(request: EmailRequest):
    try:
        # Access the correct field: request.email_content instead of request.content
        result = process_email(request.subject, request.email_content)
        
        # Handle case where no intent is identified
        if "No intent identified" in result:
            return {"classification": "No request identified", "reason": "No actionable intent in the email."}
        
        return {"classification": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the server: uvicorn main:app --host 0.0.0.0 --port 8000
