# view_audit.py
from sqlalchemy.orm import Session
from database import SessionLocal # Импортируем сессию из вашего проекта
from models import AuditLog # Импортируем модель AuditLog

def view_audit_logs():
    db: Session = SessionLocal()
    try:
        # Используем ORM для запроса к таблице audit_logs
        # order_by(-AuditLog.timestamp) сортирует по убыванию (последние первыми)
        # Если у вас нет возможности использовать -, используйте AuditLog.timestamp.desc()
        from sqlalchemy import desc
        result = db.query(AuditLog).order_by(desc(AuditLog.timestamp)).all()

        if result:
            print("Записи аудита (последние первыми):")
            for row in result:
                print(f"ID: {row.id}, User ID: {row.user_id}, Action: {row.action}, Timestamp: {row.timestamp}, Details: {row.details}")
        else:
            print("Записей аудита нет.")
    except Exception as e:
        print(f"Ошибка при чтении аудита: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    view_audit_logs()