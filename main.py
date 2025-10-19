# main.py

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from fastapi.security import OAuth2PasswordRequestForm
import io

import models, schemas, auth, audit, logic_stub
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="ЕАИС API")

# Настройка CORS
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/token", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db = next(get_db())
    try:
        db_user = auth.authenticate_user(db, form_data.username, form_data.password)
        if not db_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        token = auth.create_access_token(data={"sub": form_data.username})
        audit.log_action(db, db_user.id, "login")
        return {"access_token": token, "token_type": "bearer"}
    finally:
        db.close()

# --- НОВЫЙ ЭНДПОИНТ ДЛЯ ГЕНЕРАЦИИ PDF ---
@app.post("/generate_report")
def generate_report(request: schemas.TTRequest):
    """
    Этот эндпоинт принимает данные запроса,
    вызывает логику из logic_stub.evaluate_tt_measure,
    генерирует PDF-отчёт и возвращает его.
    """
    # Вызываем логику из logic_stub с данными запроса
    result_data = logic_stub.evaluate_tt_measure(request.tnved_code, request.product_name)

    # Генерация PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(f"ЕАИС: Отчёт по товару '{request.product_name}' (Код ТН ВЭД: {request.tnved_code})", styles['Title']))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Рекомендуемая мера ТТП:", styles['Heading2']))
    story.append(Paragraph(result_data['measure'], styles['Normal']))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Обоснование:", styles['Heading2']))
    story.append(Paragraph(result_data['reason'], styles['Normal']))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Метрики:", styles['Heading2']))
    # Простой способ вывести метрики - как строку
    metrics_str = str(result_data['metrics'])
    story.append(Paragraph(metrics_str, styles['Normal']))
    story.append(Spacer(1, 12))

    doc.build(story)
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=report_{request.tnved_code}.pdf"})

# --- ОБНОВЛЁННЫЙ ЭНДПОИНТ /evaluate ---
@app.post("/evaluate")
def evaluate(
    request: schemas.TTRequest,
    db: Session = Depends(get_db)
):
    # Вызываем обновлённую логику
    result_data = logic_stub.evaluate_tt_measure(request.tnved_code, request.product_name)

    # Возвращаем результат, включая метрики и графики (если они есть в ответе logic_stub)
    return result_data
# ---
