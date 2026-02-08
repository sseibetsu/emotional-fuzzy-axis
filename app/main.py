from fastapi import FastAPI, WebSocket, Query
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from app.ml_engine import EmotionArchitect
from app.services.gemini_client import generate_adaptive_response
from app.memory_engine import LongTermMemory
from app.services.pdf_builder import PDFReportGenerator
import json

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

ai_engine = None
memory_system = None


@app.on_event("startup")
async def startup_event():
    global ai_engine, memory_system
    ai_engine = EmotionArchitect()
    memory_system = LongTermMemory()


@app.get("/")
async def get():
    with open("static/index.html", "r", encoding='utf-8') as f:
        return HTMLResponse(f.read())


@app.get("/report")
async def get_report(session_id: str = Query(..., description="ID сессии")):
    history = memory_system.get_session_history(session_id)

    emotions = []
    for item in history:
        if item['isUser']:
            emotions.append(item.get('emotion', 'neutral'))

    pdf_gen = PDFReportGenerator("session_report.pdf")
    file_path = pdf_gen.generate(emotions)
    return FileResponse(file_path, media_type='application/pdf', filename="My_Analysis.pdf")


@app.get("/history/{session_id}")
async def get_history(session_id: str):
    """Возвращает историю чата при обновлении страницы"""
    return memory_system.get_session_history(session_id)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, session_id: str = Query(...)):
    await websocket.accept()
    try:
        while True:
            user_text = await websocket.receive_text()

            # 1. Анализ (RoBERTa)
            analysis = ai_engine.get_coordinates(user_text)

            # 2. Память (RAG)
            past_context = memory_system.get_relevant_context(
                session_id, user_text)

            # 3. Генерация (Gemini)
            ai_response = await generate_adaptive_response(user_text, analysis, past_context)

            # 4. Сохранение
            memory_system.save_memory(
                session_id, user_text, "User", analysis['dominant_emotion']
            )
            memory_system.save_memory(
                session_id, ai_response, "AI Therapist", "adaptive"
            )

            # 5. Ответ
            response_data = {
                "type": "ai_message",
                "content": ai_response,
                "meta": {
                    "graph_type": analysis['graph'],
                    "emotion": analysis['dominant_emotion'],
                    "x_val": analysis['x_val'],
                    "y_val": analysis['y_val'],
                    "breakdown": analysis.get('breakdown', [])
                }
            }
            await websocket.send_text(json.dumps(response_data))

    except Exception as e:
        print(f"WS Error: {e}")
