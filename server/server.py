from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from env import load_server_env

load_server_env()

from routes import register_routes
from utils import CORS_ALLOWED_ORIGINS, STATIC_FOLDER

server = FastAPI(title='OCR Service', version='1.0.0')

server.add_middleware(
    CORSMiddleware,
    allow_origins=list(CORS_ALLOWED_ORIGINS),
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

server.mount(
    "/static",
    StaticFiles(directory=STATIC_FOLDER),
    name="static",
)

register_routes(server)
