import os
import json
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from groq import AsyncGroq

app = FastAPI()

# Directory settings (Dhyan rahe static/templates folders honay chahiye)
# app.mount("/static", StaticFiles(directory="static"), name="static")
# templates = Jinja2Templates(directory="templates")

# Client Initialize
client = AsyncGroq(api_key=os.environ.get("GROQ_API_KEY"))

class QuizRequest(BaseModel):
    subject: str
    questions: int
    difficulty: str

@app.get("/")
async def root():
    return {"message": "Quiz API is online!"}

@app.post("/generate-quiz")
async def generate_quiz(data: QuizRequest):
    prompt = f"""
    Generate exactly {data.questions} multiple choice questions for subject: {data.subject} 
    with difficulty level: {data.difficulty}.
    Return valid JSON list of objects with keys: "question", "options" (list of 4 strings), "answer".
    No markdown, no extra text.
    """

    try:
        chat_completion = await client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a quiz generator. Always return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant"
        )

        raw_content = chat_completion.choices[0].message.content.strip()
        quiz_data = json.loads(raw_content)
        
        return {"quiz": quiz_data if isinstance(quiz_data, list) else quiz_data.get("quiz", [])}

    except Exception as e:
        return {"quiz": [], "error": str(e)}