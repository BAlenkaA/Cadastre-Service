import os

from dotenv import load_dotenv
from fastapi import FastAPI

from app.api import api_router


load_dotenv()

TITLE = os.getenv('TITLE')

app = FastAPI(title=TITLE)

app.include_router(api_router)
