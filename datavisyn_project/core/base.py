from contextlib import asynccontextmanager
from fastapi import FastAPI
from datavisyn_project.app import file_api
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
app = FastAPI()

@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend())
    
app.include_router(file_api.router, prefix="/api")