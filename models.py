from pydantic import BaseModel, Field, BeforeValidator
from typing import Optional, List, Annotated
from datetime import datetime

# Хелпер для обработки ObjectId из MongoDB
PyObjectId = Annotated[str, BeforeValidator(str)]


# --- AUTH MODELS ---
class UserRegister(BaseModel):
    nickname: str
    password: str


class UserLogin(BaseModel):
    nickname: str
    password: str


class UserResponse(BaseModel):
    id: PyObjectId = Field(alias="_id")
    nickname: str
    email: Optional[str] = "user@example.com"

    # 🔥 ВАЖНО: Добавили эти поля для работы с Flutter
    token: Optional[str] = None
    lionName: Optional[str] = "Arsik"

    level: int = 1
    xp: int = 0
    knowledgeCoins: int = 0
    currentStreak: int = 0
    inventory: List[str] = []

    # Статы
    statLogic: int = 20
    statCreativity: int = 20
    statSpeed: int = 20
    statDiscipline: int = 20

    lastLoginDate: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


# --- LION MODELS ---
class LionResponse(BaseModel):
    id: Optional[str] = None
    userId: str
    name: str = "Arsik"
    happiness: int = 50
    hunger: int = 50
    stage: str = "cub"  # cub, adolescent, adult
    mood: str = "happy"
    currentRoom: str = "yurt"
    unlockedClothing: List[str] = []
    unlockedRooms: List[str] = ["yurt"]
    currentClothing: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

    class Config:
        populate_by_name = True


# --- SHOP MODELS ---
class BuyRequest(BaseModel):
    userId: str
    itemId: str
    price: int
    category: str = "item"


# --- AI MODELS ---
class ChatRequest(BaseModel):
    userId: str
    message: str
    language: str = "ru"


# --- GAME MODELS (ДОБАВЛЕНО) ---
class LevelCompleteRequest(BaseModel):
    userId: str
    levelId: str