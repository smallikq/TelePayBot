import aiosqlite
import logging
from typing import List, Optional
from models import Payment
from datetime import datetime
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class Database:
    
    def __init__(self, db_path: str = "bot_database.db"):
        self.db_path = db_path
        self._connection = None
    
    @asynccontextmanager
    async def get_connection(self):
        conn = None
        try:
            conn = await aiosqlite.connect(self.db_path)
            conn.row_factory = aiosqlite.Row
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                await conn.close()
    
    
    async def init_db(self):
        try:
            async with self.get_connection() as db:
                # Таблица сотрудников
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS employees (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        added_at TIMESTAMP NOT NULL,
                        added_by INTEGER NOT NULL,
                        is_active INTEGER DEFAULT 1
                    )
                """)
                
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
                        replied INTEGER DEFAULT 0,
                        employee_message_id INTEGER,
                        created_at TIMESTAMP NOT NULL,
                        paid_at TIMESTAMP
                    )
                """)
                
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_employee_status 
                    ON payments(employee_id, status)
                """)
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_status 
                    ON payments(status)
                """)
                
                try:
                    await db.execute("ALTER TABLE payments ADD COLUMN replied INTEGER DEFAULT 0")
                except:
                    pass
                try:
                    await db.execute("ALTER TABLE payments ADD COLUMN employee_message_id INTEGER")
                except:
                    pass
                    
                await db.commit()
                logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    
    async def create_payment(self, payment: Payment) -> int:
        try:
            async with self.get_connection() as db:
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
                payment_id = cursor.lastrowid
                logger.info(f"Created payment request #{payment_id} for user {payment.employee_id}")
                return payment_id
        except Exception as e:
            logger.error(f"Failed to create payment: {e}")
            raise
    
    
    async def get_payment_by_id(self, payment_id: int) -> Optional[Payment]:
        try:
            async with self.get_connection() as db:
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
                        replied=bool(row['replied']) if 'replied' in row.keys() else False,
                        employee_message_id=row['employee_message_id'] if 'employee_message_id' in row.keys() else None,
                        created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                        paid_at=datetime.fromisoformat(row['paid_at']) if row['paid_at'] else None
                    )
                return None
        except Exception as e:
            logger.error(f"Failed to get payment #{payment_id}: {e}")
            return None
    
    
    async def get_user_pending_payments(self, employee_id: int) -> List[Payment]:
        try:
            async with self.get_connection() as db:
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
                        replied=bool(row['replied']) if 'replied' in row.keys() else False,
                        employee_message_id=row['employee_message_id'] if 'employee_message_id' in row.keys() else None,
                        created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                        paid_at=datetime.fromisoformat(row['paid_at']) if row['paid_at'] else None
                    ))
                return payments
        except Exception as e:
            logger.error(f"Failed to get pending payments for user {employee_id}: {e}")
            return []
    
    
    async def update_payment_status(self, payment_id: int, status: str, payment_amount: int) -> None:
        try:
            async with self.get_connection() as db:
                await db.execute(
                    "UPDATE payments SET status = ?, payment_amount = ?, paid_at = ? WHERE id = ?",
                    (status, payment_amount, datetime.now(), payment_id)
                )
                await db.commit()
                logger.info(f"Updated payment #{payment_id} to status '{status}' with amount {payment_amount}")
        except Exception as e:
            logger.error(f"Failed to update payment #{payment_id} status: {e}")
            raise
    
    async def update_payment_replied(self, payment_id: int) -> None:
        try:
            async with self.get_connection() as db:
                await db.execute(
                    "UPDATE payments SET replied = 1 WHERE id = ?",
                    (payment_id,)
                )
                await db.commit()
                logger.info(f"Updated payment #{payment_id} replied status")
        except Exception as e:
            logger.error(f"Failed to update payment #{payment_id} replied status: {e}")
            raise
    
    async def update_employee_message_id(self, payment_id: int, message_id: int) -> None:
        try:
            async with self.get_connection() as db:
                await db.execute(
                    "UPDATE payments SET employee_message_id = ? WHERE id = ?",
                    (message_id, payment_id)
                )
                await db.commit()
        except Exception as e:
            logger.error(f"Failed to update employee message ID for payment #{payment_id}: {e}")
            raise
    
    async def delete_payment(self, payment_id: int, employee_id: int) -> bool:
        try:
            async with self.get_connection() as db:
                cursor = await db.execute(
                    "DELETE FROM payments WHERE id = ? AND employee_id = ? AND status = 'pending'",
                    (payment_id, employee_id)
                )
                await db.commit()
                success = cursor.rowcount > 0
                if success:
                    logger.info(f"Deleted payment #{payment_id} for user {employee_id}")
                return success
        except Exception as e:
            logger.error(f"Failed to delete payment #{payment_id}: {e}")
            return False
    
    async def get_statistics(self, days: int = 30) -> dict:
        try:
            async with self.get_connection() as db:
                cursor = await db.execute(
                    """SELECT COUNT(*) as total, SUM(payment_amount) as total_amount
                       FROM payments 
                       WHERE status = 'paid' 
                       AND paid_at >= datetime('now', '-' || ? || ' days')""",
                    (days,)
                )
                row = await cursor.fetchone()
                
                stats = {
                    'total_paid': row['total'] or 0,
                    'total_amount': row['total_amount'] or 0,
                    'pending': 0,
                    'by_employee': {}
                }
                
                cursor = await db.execute(
                    "SELECT COUNT(*) as pending FROM payments WHERE status = 'pending'"
                )
                row = await cursor.fetchone()
                stats['pending'] = row['pending'] or 0
                
                cursor = await db.execute(
                    """SELECT employee_id, employee_username, 
                              COUNT(*) as count, SUM(payment_amount) as amount
                       FROM payments 
                       WHERE status = 'paid' 
                       AND paid_at >= datetime('now', '-' || ? || ' days')
                       GROUP BY employee_id
                       ORDER BY amount DESC""",
                    (days,)
                )
                rows = await cursor.fetchall()
                for row in rows:
                    stats['by_employee'][row['employee_id']] = {
                        'username': row['employee_username'],
                        'count': row['count'],
                        'amount': row['amount'] or 0
                    }
                
                return stats
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {
                'total_paid': 0,
                'total_amount': 0,
                'pending': 0,
                'by_employee': {}
            }
    
    async def close(self) -> None:
        if self._connection:
            await self._connection.close()
            logger.info("Database connection closed")
    
    # Методы для управления сотрудниками
    
    async def add_employee(self, user_id: int, username: str = None, first_name: str = None, added_by: int = 0) -> bool:
        """Добавить сотрудника в базу данных"""
        try:
            async with self.get_connection() as db:
                await db.execute("""
                    INSERT OR REPLACE INTO employees (user_id, username, first_name, added_at, added_by, is_active)
                    VALUES (?, ?, ?, ?, ?, 1)
                """, (user_id, username, first_name, datetime.now(), added_by))
                await db.commit()
                logger.info(f"Added employee {user_id} (@{username}) by admin {added_by}")
                return True
        except Exception as e:
            logger.error(f"Failed to add employee {user_id}: {e}")
            return False
    
    async def remove_employee(self, user_id: int) -> bool:
        """Удалить сотрудника из базы данных"""
        try:
            async with self.get_connection() as db:
                await db.execute(
                    "UPDATE employees SET is_active = 0 WHERE user_id = ?",
                    (user_id,)
                )
                await db.commit()
                logger.info(f"Removed employee {user_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to remove employee {user_id}: {e}")
            return False
    
    async def get_all_employees(self) -> List[dict]:
        """Получить список всех активных сотрудников"""
        try:
            async with self.get_connection() as db:
                cursor = await db.execute(
                    "SELECT * FROM employees WHERE is_active = 1 ORDER BY added_at DESC"
                )
                rows = await cursor.fetchall()
                employees = []
                for row in rows:
                    employees.append({
                        'user_id': row['user_id'],
                        'username': row['username'],
                        'first_name': row['first_name'],
                        'added_at': datetime.fromisoformat(row['added_at']) if row['added_at'] else None
                    })
                return employees
        except Exception as e:
            logger.error(f"Failed to get employees: {e}")
            return []
    
    async def is_employee(self, user_id: int) -> bool:
        """Проверить, является ли пользователь сотрудником"""
        try:
            async with self.get_connection() as db:
                cursor = await db.execute(
                    "SELECT user_id FROM employees WHERE user_id = ? AND is_active = 1",
                    (user_id,)
                )
                row = await cursor.fetchone()
                return row is not None
        except Exception as e:
            logger.error(f"Failed to check employee {user_id}: {e}")
            return False
    
    async def get_employee_count(self) -> int:
        """Получить количество активных сотрудников"""
        try:
            async with self.get_connection() as db:
                cursor = await db.execute(
                    "SELECT COUNT(*) as count FROM employees WHERE is_active = 1"
                )
                row = await cursor.fetchone()
                return row['count'] if row else 0
        except Exception as e:
            logger.error(f"Failed to get employee count: {e}")
            return 0
    
    async def get_employee_name(self, user_id: int) -> Optional[str]:
        """Получить имя сотрудника"""
        try:
            async with self.get_connection() as db:
                cursor = await db.execute(
                    "SELECT first_name FROM employees WHERE user_id = ? AND is_active = 1",
                    (user_id,)
                )
                row = await cursor.fetchone()
                return row['first_name'] if row else None
        except Exception as e:
            logger.error(f"Failed to get employee name for {user_id}: {e}")
            return None

