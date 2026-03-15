import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# --- CORS SETUP ---
# This allows your HTML file to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins, change to specific URL for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Clients
# The new SDK uses genai.Client
gemini_client = genai.Client(api_key=GEMINI_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class UserStats(BaseModel):
    weight: float
    height: float
    age: int
    goal: str

@app.post("/recommendation")
async def get_health_plan(stats: UserStats):
    try:
        # 1. Generate the Health Plan using the new SDK syntax
        prompt = (
            f"User Profile: Age {stats.age}, Weight {stats.weight}kg, Height {stats.height}cm. "
            f"Goal: {stats.goal}. Provide a concise, professional diet and sleep plan."
        )
        
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash", # Updated to the latest stable model
            contents=prompt
        )
        recommendation_text = response.text

        # 2. Save Data to Supabase
        db_data = {
            "weight": stats.weight,
            "height": stats.height,
            "age": stats.age,
            "goal": stats.goal,
            "recommendation": recommendation_text
        }
        
        supabase.table("user_health_data").insert(db_data).execute()

        # 3. Return response to Frontend
        return {
            "status": "success",
            "plan": recommendation_text
        }

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Run using: uvicorn main:app --reload