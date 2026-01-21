import asyncio
from database import users_collection


async def give_money():
    # 👇 Впиши сюда точный никнейм, который ты использовал в приложении
    nickname = "ТвойНик"

    # Начисляем 5000 монет
    result = await users_collection.update_one(
        {"nickname": nickname},
        {"$set": {"knowledgeCoins": 5000}}
    )

    if result.matched_count > 0:
        print(f"💰 Успешно! Пользователю {nickname} начислено 5000 монет.")
    else:
        print(f"❌ Пользователь '{nickname}' не найден. Проверь, правильно ли написал ник!")


if __name__ == "__main__":
    asyncio.run(give_money())