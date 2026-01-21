import asyncio
from database import db

# --- КОНФИГУРАЦИЯ ---
LEVELS_COUNT = 20  # Количество уровней в каждой карте

# Список всех направлений (10 категорий * 5 специализаций)
# ID должны совпадать с теми, что используются во Flutter (specializations_data.dart)
ALL_SPECS = {
    # 1. IT
    "it": [
        {"id": "it_cs", "name": "Computer Science"},
        {"id": "it_py", "name": "Python Backend"},
        {"id": "it_fe", "name": "Frontend Web"},
        {"id": "it_mob", "name": "Mobile Dev"},
        {"id": "it_game", "name": "Game Dev (Unity/UE)"},
    ],
    # 2. Языки
    "languages": [
        {"id": "lang_eng_kick", "name": "English: Start"},
        {"id": "lang_eng_pro", "name": "English: Pro"},
        {"id": "lang_jap", "name": "Японский язык"},
        {"id": "lang_kor", "name": "Корейский язык"},
        {"id": "lang_chi", "name": "Китайский язык"},
    ],
    # 3. Soft Skills
    "soft_skills": [
        {"id": "soft_comm", "name": "Коммуникация"},
        {"id": "soft_lead", "name": "Лидерство"},
        {"id": "soft_time", "name": "Тайм-менеджмент"},
        {"id": "soft_emo", "name": "Эмоциональный интеллект"},
        {"id": "soft_crit", "name": "Критическое мышление"},
    ],
    # 4. Финансы
    "finance": [
        {"id": "fin_budget", "name": "Личный бюджет"},
        {"id": "fin_invest", "name": "Инвестиции"},
        {"id": "fin_crypto", "name": "Криптовалюты"},
        {"id": "fin_trade", "name": "Трейдинг"},
        {"id": "fin_bus", "name": "Финансы бизнеса"},
    ],
    # 5. Здоровье
    "health": [
        {"id": "health_sleep", "name": "Здоровый Сон"},
        {"id": "health_nutri", "name": "Правильное Питание"},
        {"id": "health_sport", "name": "Фитнес и Спорт"},
        {"id": "health_men", "name": "Ментальное здоровье"},
        {"id": "health_bio", "name": "Биохакинг"},
    ],
    # 6. Искусство
    "art": [
        {"id": "art_design", "name": "Графический Дизайн"},
        {"id": "art_history", "name": "История Искусств"},
        {"id": "art_draw", "name": "Рисование"},
        {"id": "art_photo", "name": "Фотография"},
        {"id": "art_music", "name": "Теория Музыки"},
    ],
    # 7. Наука
    "science": [
        {"id": "sci_math", "name": "Математика"},
        {"id": "sci_phys", "name": "Физика"},
        {"id": "sci_chem", "name": "Химия"},
        {"id": "sci_bio", "name": "Биология"},
        {"id": "sci_astro", "name": "Астрономия"},
    ],
    # 8. Психология
    "psychology": [
        {"id": "psy_base", "name": "Основы Психологии"},
        {"id": "psy_rel", "name": "Отношения"},
        {"id": "psy_self", "name": "Самопознание"},
        {"id": "psy_cog", "name": "Когнитивистика"},
        {"id": "psy_soc", "name": "Социальная психология"},
    ],
    # 9. Карьера
    "career": [
        {"id": "car_job", "name": "Поиск Работы"},
        {"id": "car_brand", "name": "Личный Бренд"},
        {"id": "car_freelance", "name": "Фриланс"},
        {"id": "car_start", "name": "Стартапы"},
        {"id": "car_neg", "name": "Переговоры"},
    ],
    # 10. Стратегия
    "strategy": [
        {"id": "str_game", "name": "Теория Игр"},
        {"id": "str_dec", "name": "Принятие Решений"},
        {"id": "str_chess", "name": "Шахматы"},
        {"id": "str_poker", "name": "Покер (Математика)"},
        {"id": "str_war", "name": "Искусство Войны"},
    ],
}


def generate_levels_for_spec(spec_id, spec_name):
    """
    Генерирует 20 уровней для конкретного направления.
    """
    levels = []
    for i in range(1, LEVELS_COUNT + 1):
        # Первый уровень всегда открыт, остальные закрыты
        is_unlocked = (i == 1)

        level = {
            "id": f"{spec_id}_lvl_{i}",
            "number": i,
            "title": f"Уровень {i}: Основы {spec_name}",
            "description": f"Введение в тему уровня {i}. Изучите материалы и пройдите тест, чтобы продвинуться дальше.",
            "is_unlocked": is_unlocked,
            "is_completed": False
        }
        levels.append(level)
    return levels


async def seed():
    print("🗑️  Очистка старой базы данных...")
    # Удаляем ВСЕ старые карты, чтобы не было дублей
    await db.roadmaps.delete_many({})

    print(f"🌱 Начинаем генерацию: 10 категорий x 5 направлений x {LEVELS_COUNT} уровней...")

    count = 0

    for category, specs in ALL_SPECS.items():
        for spec in specs:
            spec_id = spec["id"]
            spec_name = spec["name"]

            # Генерируем объект Roadmap
            roadmap = {
                "field_id": spec_id,  # ID, по которому ищет API (/roadmap/{field_id})
                "field_name": spec_name,  # Красивое название
                "total_levels": LEVELS_COUNT,
                "levels": generate_levels_for_spec(spec_id, spec_name)
            }

            # Вставляем в БД
            await db.roadmaps.insert_one(roadmap)
            count += 1
            print(f"   ✅ Создана карта: {spec_name} ({spec_id})")

    print(f"\n🎉 Успешно! Добавлено {count} дорожных карт в базу данных.")
    print("Теперь перезапустите Flutter приложение, и ошибки 404 исчезнут.")


if __name__ == "__main__":
    asyncio.run(seed())