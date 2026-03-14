from fastapi import FastAPI
from pydantic import BaseModel
import google.generativeai as genai
from supabase import create_client

app = FastAPI()

# Configuration
genai.configure(api_key="AIzaSyDc2St8cL3M2mT7fjpSJrZQdbguFlquTAs")
supabase = create_client("URL", "KEY")

class UserStats(BaseModel):
    weight: float
    height: float
    age: int
    goal: str # e.g., "lose weight", "muscle gain"

@app.post("/recommendation")
async def get_health_plan(stats: UserStats):
    # 1. Save to Supabase (Optional but recommended)
    # supabase.table("user_metrics").insert(stats.dict()).execute()

    # 2. Construct the Prompt
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"User is {stats.age}y/o, {stats.weight}kg, and {stats.height}cm tall. Goal: {stats.goal}. Provide a concise diet and sleep plan."
    
    response = model.generate_content(prompt)
    
    return {"plan": response.text}