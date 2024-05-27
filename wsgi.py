# wsgi.py
from app.main import app  # FastAPI 애플리케이션 객체 가져오기

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)