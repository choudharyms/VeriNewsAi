from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os

# Load environment variables early
load_dotenv()

from routes import health, analysis
from utils.logger import logger
import uvicorn

app = FastAPI(
    title="VeriNewsAI",
    description="AI-powered fake news detection system",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Error Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled Global Exception", path=request.url.path, error=str(exc))
    return JSONResponse(
        status_code=500,
        content={"detail": "Something went wrong. Please try again later."}
    )

# Lifecycle events
@app.on_event("startup")
async def startup_event():
    logger.info("VeriNewsAI Server Sparking Up...")
    pass

# Include routes
app.include_router(health.router)
app.include_router(analysis.router)

# Serve static files
# app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def serve_index():
    return FileResponse("frontend/index.html")

@app.get("/analysis")
async def serve_analysis():
    return FileResponse("frontend/analysis.html")

@app.get("/archive")
async def serve_archive():
    return FileResponse("frontend/archive.html")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
