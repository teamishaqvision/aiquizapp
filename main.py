from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import requests
import json

app = FastAPI()

# Agar static/templates folders hain, to ye lines rehne do
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

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
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "gemma4:latest", "prompt": prompt, "stream": False},
            timeout=120
        )
        raw = response.json()["response"].replace("```json", "").replace("```", "").strip()
        quiz = json.loads(raw)
        return {"quiz": quiz}
    except Exception as e:
        return {"quiz": [], "error": str(e)}