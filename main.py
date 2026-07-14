import os
import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from groq import AsyncGroq  # Groq client import kiya

app = FastAPI()

# Static aur Templates directory (jaisa aapka pehle tha)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Groq Client initialize kiya (API Key environment variable se lega)
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
    Generate exactly {data.questions} multiple choice questions.
    Subject: {data.subject}
    Difficulty: {data.difficulty}
    Return ONLY JSON.
    Example format:
    [
      {{"question": "...", "options": ["...", "...", "...", "..."], "answer": "..."}}
    ]
    Do not return markdown. Only JSON.
    """
    
    try:
        # Groq API ko call kar rahe hain
        chat_completion = await client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a quiz generator. Output ONLY valid JSON."},
                {"role": "user", "content": prompt}
            ],
            model="llama3-8b-8192", # Groq ka fast model
            response_format={"type": "json_object"}
        )
        
        # Groq ka response parse karna
        raw_content = chat_completion.choices[0].message.content
        quiz = json.loads(raw_content)
        
        # Agar JSON mein 'quiz' key nahi hai, toh dictionary structure maintain karna
        if "quiz" not in quiz:
            return {"quiz": quiz}
        return quiz

    except Exception as e:
        return {"quiz": [], "error": str(e)}