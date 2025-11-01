
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI, OpenAIError

load_dotenv()

app = FastAPI(title="Text Summarizer API")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
        response = client.chat.completions.create(
            model="gpt-4o-mini",  
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes text."},
                {"role": "user", "content": f"Summarize this text:\n{request.text}"}
            ]
        )
       
        summary = response.choices[0].message.content
        
        original_word_count = len(request.text.split())
        summary_word_count = len(summary.split()) if isinstance(summary, str) else 0
        
        return {
            "original_word_count": original_word_count,
            "summary_word_count": summary_word_count,
            "summary": summary
        }
    
    except OpenAIError as oe:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(oe)}") 
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error summarizing text: {str(e)}")