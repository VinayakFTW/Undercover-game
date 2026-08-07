from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
from dotenv import load_dotenv
import os


load_dotenv()

engine = create_engine(os.getenv("POSTGRES_URL", "sqlite:///./sbi_saarthi.db"))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
BASE = declarative_base()

from server.models.db_models import *
