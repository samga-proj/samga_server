from fastapi import APIRouter, HTTPException, status
from models import UserRegister, UserLogin, UserResponse
from database import users_collection, lions_collection
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from config import Config  # Импортируем наш конфиг

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, Config.SECRET_KEY, algorithm=Config.ALGORITHM)
    return encoded_jwt


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


# --- РУЧКИ ---
@router.post("/register", response_model=UserResponse)
async def register(user: UserRegister):
    existing_user = await users_collection.find_one({"name": user.nickname})
    if existing_user:
        raise HTTPException(status_code=400, detail="Nickname already taken")

    new_user_dict = {
        "name": user.nickname,
        "password": get_password_hash(user.password),
        "level": 1,
        "xp": 0,
        "knowledgeCoins": 100,
        "preferredLanguage": "ru",
        "currentStreak": 1,
        "longestStreak": 1,
        "lastLoginDate": datetime.now().isoformat(),
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat()
    }

    result = await users_collection.insert_one(new_user_dict)
    user_id = str(result.inserted_id)

    # Создаем льва
    new_lion = {
        "userId": user_id,
        "name": "Arsik",
        "happiness": 80,
        "hunger": 30,
        "stage": "cub"
    }
    await lions_collection.insert_one(new_lion)

    # Генерируем токен
    access_token = create_access_token(data={"sub": user.nickname, "id": user_id})

    # Собираем ответ
    return UserResponse(
        id=user_id,
        nickname=user.nickname,
        email=f"{user.nickname}@samga.app",
        token=access_token,  # 🔥 Теперь мы реально отдаем токен
        **new_user_dict,
        lionName="Arsik"
    )


@router.post("/login", response_model=dict)  # 🔥 Меняем response_model на dict для гибкости
async def login(user: UserLogin):
    db_user = await users_collection.find_one({"name": user.nickname})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    lion = await lions_collection.find_one({"userId": str(db_user["_id"])})
    lion_name = lion["name"] if lion else "Arsik"

    access_token = create_access_token(data={"sub": db_user["name"], "id": str(db_user["_id"])})

    # Формируем ответ, понятный для Flutter (учитывая путаницу с access_token/token)
    response_data = UserResponse(
        id=str(db_user["_id"]),
        nickname=db_user["name"],
        email=f"{db_user['name']}@samga.app",
        token=access_token,
        **db_user,
        lionName=lion_name
    ).model_dump(by_alias=True)

    # 🔥 ХАК: Дублируем токен, чтобы Flutter нашел его в любом поле
    response_data["access_token"] = access_token

    return response_data