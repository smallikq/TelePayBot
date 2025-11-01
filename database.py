import aiosqlite
from typing import List, Optional
from models import Payment
from datetime import datetime


class Database:
    """Класс для работы с SQLite базой данных"""
    
    def __init__(self, db_path: str = "bot_database.db"):
        self.db_path = db_path
    
    async def init_db(self):
        """Инициализация базы данных и создание таблиц"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER NOT NULL,
                    employee_username TEXT,
                    balance TEXT NOT NULL,
                    username_field TEXT NOT NULL,
                    screenshot_file_id TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    payment_amount INTEGER,
                    created_at TIMESTAMP NOT NULL,
                    paid_at TIMESTAMP
                )
            """)
            await db.commit()
    
    async def create_payment(self, payment: Payment) -> int:
        """Создание новой заявки на оплату"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO payments (
                    employee_id, employee_username, balance, username_field,
                    screenshot_file_id, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                payment.employee_id,
                payment.employee_username,
                payment.balance,
                payment.username_field,
                payment.screenshot_file_id,
                payment.status,
                payment.created_at
            ))
            await db.commit()
            return cursor.lastrowid
    
    async def get_payment_by_id(self, payment_id: int) -> Optional[Payment]:
        """Получение заявки по ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM payments WHERE id = ?",
                (payment_id,)
            )
            row = await cursor.fetchone()
            if row:
                return Payment(
                    id=row['id'],
                    employee_id=row['employee_id'],
                    employee_username=row['employee_username'],
                    balance=row['balance'],
                    username_field=row['username_field'],
                    screenshot_file_id=row['screenshot_file_id'],
                    status=row['status'],
                    payment_amount=row['payment_amount'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                    paid_at=datetime.fromisoformat(row['paid_at']) if row['paid_at'] else None
                )
            return None
    
    async def get_user_pending_payments(self, employee_id: int) -> List[Payment]:
        """Получение всех активных заявок пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM payments WHERE employee_id = ? AND status = 'pending' ORDER BY created_at DESC",
                (employee_id,)
            )
            rows = await cursor.fetchall()
            payments = []
            for row in rows:
                payments.append(Payment(
                    id=row['id'],
                    employee_id=row['employee_id'],
                    employee_username=row['employee_username'],
                    balance=row['balance'],
                    username_field=row['username_field'],
                    screenshot_file_id=row['screenshot_file_id'],
                    status=row['status'],
                    payment_amount=row['payment_amount'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                    paid_at=datetime.fromisoformat(row['paid_at']) if row['paid_at'] else None
                ))
            return payments
    
    async def update_payment_status(self, payment_id: int, status: str, payment_amount: int):
        """Обновление статуса заявки и суммы оплаты"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE payments SET status = ?, payment_amount = ?, paid_at = ? WHERE id = ?",
                (status, payment_amount, datetime.now(), payment_id)
            )
            await db.commit()
    
    async def delete_payment(self, payment_id: int, employee_id: int) -> bool:
        """Удаление заявки (только если она принадлежит сотруднику и не оплачена)"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "DELETE FROM payments WHERE id = ? AND employee_id = ? AND status = 'pending'",
                (payment_id, employee_id)
            )
            await db.commit()
            return cursor.rowcount > 0

