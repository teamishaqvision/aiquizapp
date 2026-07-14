import os
import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from groq import AsyncGroq

app = FastAPI()

# Static aur Templates directory
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Groq Client initialize
client = AsyncGroq(api_key=os.environ.get("GROQ_API_KEY"))

class QuizRequest(BaseModel):
    subject: str
    difficulty: str
    questions: int

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/generate-quiz")
async def generate_quiz(data: QuizRequest):
    prompt = f"""
    Generate exactly {data.questions} multiple choice questions for the subject: {data.subject} 
    with difficulty level: {data.difficulty}.
    Return the response as a valid JSON list of objects.
    Each object must have these keys: "question", "options" (a list of 4 strings), and "answer".
    Do not include any other text, explanations, or markdown formatting. 
    Only return raw JSON.
    """
    
    try:
        chat_completion = await client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful quiz generator. Always return valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant"
        )
        
        raw_content = chat_completion.choices[0].message.content.strip()
        
        # JSON parse karna
        quiz_data = json.loads(raw_content)
        
        # Agar response list mein hai toh wrap karke bhejo
        return {"quiz": quiz_data if isinstance(quiz_data, list) else quiz_data.get("quiz", [])}

    except Exception as e:
        return {"quiz": [], "error": str(e)}