import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from routes import auth, lion, shop, ai, roadmap, leaderboard, news, game

app = FastAPI()

# Разрешаем запросы с любого источника (для Flutter)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем маршруты
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(lion.router, prefix="/lion", tags=["Lion"])
app.include_router(shop.router, prefix="/shop", tags=["Shop"])
app.include_router(ai.router, prefix="/ai", tags=["AI"])
app.include_router(roadmap.router, prefix="/roadmap", tags=["Roadmap"])
app.include_router(leaderboard.router, prefix="/leaderboard", tags=["Leaderboard"])
app.include_router(news.router, prefix="/news", tags=["News"])
app.include_router(game.router, prefix="/game", tags=["Game"])

if os.path.exists("web"):
    app.mount("/", StaticFiles(directory="web", html=True), name="static")

