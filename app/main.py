from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.resume_router import router as resume_router
from app.gradio_ui import create_ui
import gradio as gr
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Resume Rewriter LLM",
    description="An AI-powered resume optimization service",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create Gradio UI
ui = create_ui()
app = gr.mount_gradio_app(app, ui, path="/")

# Include API routes for programmatic access
app.include_router(resume_router, prefix="/api")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0"
    }

# Import and include routers
# This will be uncommented as we add more routes
# from app.api import resume_router, jobs_router
# app.include_router(resume_router.router)
# app.include_router(jobs_router.router) 