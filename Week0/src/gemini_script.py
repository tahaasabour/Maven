import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai

load_dotenv()

app = FastAPI(title="Text Summarizer API")

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-flash-latest')

class TextRequest(BaseModel):
    text: str

@app.get("/")
def read_root():
    return {"Welcome to Text Summarization API": "Use /summarize endpoint to summarize text."}

@app.post("/summarize")
def summarize_text(request: TextRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    
    try:
        prompt = f"Summarize the following text:\n\n{request.text}"
        response = model.generate_content(prompt)
        
        summary = response.text
        
        original_word_count = len(request.text.split())
        summary_word_count = len(summary.split()) if isinstance(summary, str) else 0
        
        return {
            "original_word_count": original_word_count,
            "summary_word_count": summary_word_count,
            "summary": summary
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error summarizing text: {str(e)}")