from fastapi import FastAPI
from src.routes.login import router
from .db import init_db
from .models import *
import os
import importlib

init_db()

app = FastAPI()

def build_routes():
    route_dir = f"{os.getcwd()}/src/routes"
    print(os.listdir(route_dir))
    for route in os.listdir(route_dir):
        if route in ['__init__.py'] or not route.endswith('.py'):
            print(f'{route} route skip')
            continue
        module = importlib.import_module(f'src.routes.{route.replace('.py', '')}')
        app.include_router(module.router, tags=[route])

build_routes()

@app.get('/')
async def get():
    return 'hello world'
