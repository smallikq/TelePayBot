"""
Скрипт миграции сотрудников из .env в базу данных
Запустите этот скрипт один раз для переноса существующих сотрудников
"""
import asyncio
import os
from dotenv import load_dotenv
from database import Database

load_dotenv()


async def migrate_employees():
    """Перенести сотрудников из EMPLOYEE_IDS в базу данных"""
    
    db = Database()
    await db.init_db()
    
    # Получаем список ID из .env
    employee_ids_str = os.getenv("EMPLOYEE_IDS", "")
    if not employee_ids_str:
        print("❌ EMPLOYEE_IDS не найден в .env файле")
        return
    
    employee_ids = [
        int(id_.strip()) 
        for id_ in employee_ids_str.split(",") 
        if id_.strip()
    ]
    
    if not employee_ids:
        print("❌ Список сотрудников пуст")
        return
    
    print(f"📋 Найдено сотрудников в .env: {len(employee_ids)}")
    print(f"🔄 Начинаем миграцию...\n")
    
    # Получаем ID первого администратора для записи в added_by
    admin_ids_str = os.getenv("ADMIN_ID", "")
    first_admin = 0
    if admin_ids_str:
        admin_ids = [int(id_.strip()) for id_ in admin_ids_str.split(",") if id_.strip()]
        if admin_ids:
            first_admin = admin_ids[0]
    
    success_count = 0
    skip_count = 0
    
    for emp_id in employee_ids:
        # Проверяем, не добавлен ли уже
        is_exists = await db.is_employee(emp_id)
        if is_exists:
            print(f"⏭️  ID {emp_id} - уже существует в базе, пропускаем")
            skip_count += 1
            continue
        
        # Добавляем в базу
        success = await db.add_employee(
            user_id=emp_id,
            username=None,  # Не знаем username из .env
            first_name=None,  # Не знаем имя из .env
            added_by=first_admin
        )
        
        if success:
            print(f"✅ ID {emp_id} - успешно добавлен")
            success_count += 1
        else:
            print(f"❌ ID {emp_id} - ошибка добавления")
    
    print(f"\n📊 Результаты миграции:")
    print(f"  ✅ Добавлено: {success_count}")
    print(f"  ⏭️  Пропущено (уже существует): {skip_count}")
    print(f"  📝 Всего обработано: {len(employee_ids)}")
    
    print("\n💡 Теперь вы можете удалить строку EMPLOYEE_IDS из .env файла")
    print("   или оставить её для совместимости (она больше не используется)")
    
    await db.close()


if __name__ == "__main__":
    print("🚀 Миграция сотрудников в базу данных\n")
    asyncio.run(migrate_employees())
    print("\n✅ Миграция завершена!")
