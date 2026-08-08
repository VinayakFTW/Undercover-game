from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
from dotenv import load_dotenv
import os


load_dotenv("D:\\Work\\Code\\AIClub\\Undercover-game\\server\\.env")

engine = create_engine(os.getenv("POSTGRES_URL"))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
BASE = declarative_base()

from server.models.db_models import *

def init_db():
    BASE.metadata.create_all(bind=engine)