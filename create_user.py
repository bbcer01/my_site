from passlib.context import CryptContext
from database import SessionLocal
import models

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

db = SessionLocal()
user = models.User(username="testuser", hashed_password=pwd_context.hash("testpassword"))
db.add(user)
db.commit()
db.close()

print("Пользователь testuser создан.")