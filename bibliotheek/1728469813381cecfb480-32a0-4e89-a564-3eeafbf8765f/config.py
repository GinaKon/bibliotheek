from dotenv import load_dotenv
import os
import redis

load_dotenv()

class Config:
    ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")  # Optional
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", "False") == "True"

    SESSION_TYPE = 'redis'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_REDIS = redis.from_url(os.getenv("SESSION_REDIS_URI", "redis://127.0.0.1:6379"))



