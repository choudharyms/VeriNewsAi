# 🛡️ VeriNewsAI - AI-Powered News Verification System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)

**VeriNewsAI** is a sophisticated, production-ready system designed to combat misinformation. By leveraging hybrid AI models, it analyzes news articles in real-time to determine their credibility.

---

## ✨ Key Features

-   **🔍 Intelligent URL Extraction**: Seamlessly extracts core article content from any URL using the `newspaper3k` library.
-   **🤖 Hybrid Multi-Model Scoring**:
    -   **AI Core (70%)**: Powered by Hugging Face's BERT-based fake news detection models.
    -   **Suspicion Engine (30%)**: Heuristic keyword-based analysis to catch common misinformation patterns.
-   **📝 LLM Explainer**: Provides human-readable, context-aware explanations for every score using **Google Gemini 1.5 Flash**.
-   **⚡ High Performance**:
    -   In-memory caching for repetitive requests.
    -   Predictive model warm-up on server startup.
-   **🛡️ Robust Design**: Structured logging, request timeouts (10s), and a reliable fallback mechanism when AI services are unreachable.

---

## 🛠️ Tech Stack

### Backend
- **Core Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Asynchronous, High-performance)
- **AI Models**: Hugging Face Inference API (BERT), Google Gemini 1.5 Flash
- **Web Scraping**: Newspaper3k
- **Data Validation**: Pydantic v2
- **Utilities**: Python-dotenv, Uvicorn, Requests

### Frontend
- **Interface**: Clean, responsive HTML/JS dashboard
- **Architecture**: Statically served from the API backend

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- API Keys for Hugging Face and Google Gemini

### Installation

1. **Clone the Repository**
   ```bash
   git clone <repo-url>
   cd VeriNewsAI
   ```

2. **Setup Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuration**
   Create a `.env` file in the root directory:
   ```env
   HF_API_KEY=your_huggingface_inference_api_key
   GEMINI_API_KEY=your_google_gemini_api_key
   PORT=8000
   ```

5. **Fire it up!**
   ```bash
   python main.py
   ```
   Server will start at `http://localhost:8000`.

---

## 🔌 API Reference

### Health Check
`GET /health`
- **Description**: Returns the system status and model readiness.

### Analyze News
`POST /analyze`
- **Body**:
  ```json
  {
    "url": "https://example-news.com/article-123",
    "detailed": true
  }
  ```
- **Sample Response**:
  ```json
  {
    "result": "Fake",
    "score": 88,
    "confidence": "High",
    "explanation": "The article uses highly sensationalized language and lacks citations from verified sources...",
    "source": "url",
    "processing_time_ms": 1150
  }
  ```

---

## 📂 Project Structure

```text
VeriNewsAI/
├── frontend/          # Web dashboard (HTML/JS/CSS)
├── routes/            # FastAPI API routers
├── services/          # Business logic (Scraper, AI Detector, Explainer)
├── utils/             # Logging, Caching, and Text Processing
├── main.py            # Application entry point & configuration
├── requirements.txt   # Backend dependencies
└── render.yaml        # Deployment configuration
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Developed with ❤️ for a more informed world.
