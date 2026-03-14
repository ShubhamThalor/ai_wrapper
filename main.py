import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Configuration using environment variables
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Clients
genai.configure(api_key=GEMINI_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class UserStats(BaseModel):
    weight: float
    height: float
    age: int
    goal: str

@app.post("/recommendation")
async def get_health_plan(stats: UserStats):
    try:
        # 1. Generate the Health Plan using Gemini
        model = genai.GenerativeModel('gemini-1.5-flash') # Using the faster flash model
        prompt = (
            f"User Profile: Age {stats.age}, Weight {stats.weight}kg, Height {stats.height}cm. "
            f"Goal: {stats.goal}. Provide a concise, professional diet and sleep plan."
        )
        
        response = model.generate_content(prompt)
        recommendation_text = response.text

        # 2. Save Data & Recommendation to Supabase
        db_data = {
            "weight": stats.weight,
            "height": stats.height,
            "age": stats.age,
            "goal": stats.goal,
            "recommendation": recommendation_text
        }
        
        # Ensure the table name matches what you created (e.g., 'user_health_data')
        supabase.table("user_health_data").insert(db_data).execute()

        # 3. Return response to Frontend
        return {
            "status": "success",
            "plan": recommendation_text
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# To run: uvicorn main:app --reload