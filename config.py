import os
from dotenv import load_dotenv

load_dotenv()

API_NAME = "Task Manager"
LIST_OFFSET = int(os.getenv("LIST_OFFSET", "0"))
LIST_LIMIT = int(os.getenv("LIST_LIMIT", "10"))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, os.getenv("DB_PATH", "task.db"))
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")
