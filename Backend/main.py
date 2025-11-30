from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pypdf
import io
import os
# import google.generativeai as genai # Uncomment if using Gemini
# from openai import OpenAI # Uncomment if using OpenAI

app = FastAPI()

# Configure CORS to allow React to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"], # Common React ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- AI Configuration (Placeholder) ---
# You need to install the SDK for your chosen AI (Gemini or OpenAI)
# and set your API key here.

def query_ai_for_questions(text: str):
    """
    Sends the text to an AI model to generate questions.
    Replace this logic with your actual AI call.
    """
    
    # 1. Example using Google Gemini (Free tier available)
    # genai.configure(api_key="YOUR_API_KEY")
    # model = genai.GenerativeModel('gemini-pro')
    # prompt = f"Generate 3 short quiz questions based on this text. Return only the questions:\n\n{text}"
    # response = model.generate_content(prompt)
    # return response.text.split('\n')
    
    # 2. Example Mock Response (so the code runs without an API key immediately)
    return [
        f"Mock Question 1 based on text length {len(text)}",
        "Mock Question 2: What is the main idea?",
        "Mock Question 3: Explain the second paragraph."
    ]

@app.post("/generate-questions")
async def generate_questions(
    file: UploadFile = File(...), 
    page_number: int = Form(...)
):
    try:
        # 1. Read the uploaded PDF file
        content = await file.read()
        pdf_file = io.BytesIO(content)
        
        # 2. Parse PDF using pypdf
        reader = pypdf.PdfReader(pdf_file)
        
        # Check if page number is valid (0-indexed logic)
        idx = page_number - 1
        if idx < 0 or idx >= len(reader.pages):
            raise HTTPException(status_code=400, detail="Page number out of range")
            
        # 3. Extract text
        page = reader.pages[idx]
        text = page.extract_text()
        
        if not text or len(text.strip()) < 50:
            return {"questions": ["Not enough text on this page to generate questions."]}

        # 4. Generate questions using AI
        questions_list = query_ai_for_questions(text)
        
        # Clean up list (remove empty strings or bullet points if AI adds them)
        clean_questions = [q.strip().lstrip('- ').lstrip('123. ') for q in questions_list if q.strip()]

        return {"questions": clean_questions}

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)