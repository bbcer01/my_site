from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

import models, schemas, auth, audit, logic_stub
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="ЕАИС API")

# Настройка CORS для Wix (замените на ваш домен при развертывании)
origins = [
    "https://your-wix-site.com",  # Замените на ваш домен
    "http://localhost:3000",      # Для локальной разработки
    "https://www.wix.com",
    "https://editor.wix.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/token", response_model=schemas.Token)
def login(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = auth.authenticate_user(db, user.username, user.password)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = auth.create_access_token(data={"sub": user.username})
    audit.log_action(db, db_user.id, "login")
    return {"access_token": token, "token_type": "bearer"}

@app.post("/evaluate", response_model=schemas.TTResponse)
def evaluate(
    request: schemas.TTRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    result = logic_stub.evaluate_tt_measure(request.tnved_code, request.product_name)
    audit.log_action(db, current_user.id, "evaluate_request", f"Product: {request.product_name}, TNVED: {request.tnved_code}")
    return result