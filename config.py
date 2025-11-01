import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Bot configuration"""
    
    # Bot token
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    
    # Administrator IDs (can specify multiple separated by comma)
    ADMIN_IDS: List[int] = [
        int(id_.strip()) 
        for id_ in os.getenv("ADMIN_ID", "").split(",") 
        if id_.strip()
    ]
    
    # Group chat ID for notifications
    GROUP_CHAT_ID: int = int(os.getenv("GROUP_CHAT_ID", "0"))
    
    # Employee IDs list
    EMPLOYEE_IDS: List[int] = [
        int(id_.strip()) 
        for id_ in os.getenv("EMPLOYEE_IDS", "").split(",") 
        if id_.strip()
    ]
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that all required settings are present"""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN не установлен в .env файле")
        if not cls.ADMIN_IDS:
            raise ValueError("ADMIN_ID не установлен в .env файле")
        if not cls.GROUP_CHAT_ID:
            raise ValueError("GROUP_CHAT_ID не установлен в .env файле")
        if not cls.EMPLOYEE_IDS:
            raise ValueError("EMPLOYEE_IDS не установлен в .env файле")
        return True
    
    @classmethod
    def is_employee(cls, user_id: int) -> bool:
        """Check if user is an employee"""
        return user_id in cls.EMPLOYEE_IDS
    
    @classmethod
    def is_admin(cls, user_id: int) -> bool:
        """Check if user is an administrator"""
        return user_id in cls.ADMIN_IDS

