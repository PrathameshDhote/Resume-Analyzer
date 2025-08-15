import os
import asyncio
import logging
import json
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any

from parse import build_resume_chunks, extract_resume_text
from LLM import analyze_resume, ResumeAnalysis, AgentState

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- FastAPI App Setup ---
app = FastAPI(
    title="AI Resume Analysis Backend",
    description="Extracts resume content and analyzes it against a job description.",
    version="1.0.0"
)

origins = ["http://localhost:3000", "*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request & Response Schemas ---
class AnalyzeRequest(BaseModel):
    job_description: str

class AnalyzeResponse(BaseModel):
    analysis: ResumeAnalysis

# --- Endpoint: Health Check ---
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# --- Endpoint: Upload & Analyze Resume ---
@app.post("/analyze-resume", response_model=AnalyzeResponse)
async def upload_and_analyze(
    job_description: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Upload a resume PDF and job description.
    Parses the PDF, optionally chunks it, then analyzes via LLM.
    """
    # 1. Save uploaded file
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    logger.info(f"Saved resume to {file_path}")

    # 2. Extract & chunk resume
    try:
        chunks = build_resume_chunks(file_path, max_tokens=500)
        resume_text = "\n\n".join(c["text"] for c in chunks)
    except Exception as e:
        logger.warning(f"Chunking failed ({e}); using raw text only.")
        resume_text = extract_resume_text(file_path)

    # 3. Create state and call LLM analysis
    state = AgentState(
        query="Resume Analysis",
        resume_text=resume_text,
        job_description=job_description
    )
    result = await analyze_resume(state)

    if result.get("error"):
        logger.error(f"Analysis error: {result['error']}")
        raise HTTPException(status_code=500, detail=result["error"])

    # 4. Return only the analysis
    return AnalyzeResponse(analysis=result["analysis_result"])

# --- Run with Uvicorn if executed directly ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
