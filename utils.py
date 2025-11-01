"""Utility functions for the bot"""
import re
from typing import Tuple


class Validator:
    
    @staticmethod
    def validate_balance(balance: str) -> Tuple[bool, str]:
        if not balance or not balance.strip():
            return False, "Баланс не может быть пустым"
        
        if len(balance) > 50:
            return False, "Баланс слишком длинный (максимум 50 символов)"
        
        if not any(char.isdigit() for char in balance):
            return False, "Баланс должен содержать числовое значение"
        
        return True, ""
    
    @staticmethod
    def validate_username(username: str) -> Tuple[bool, str]:
        if not username or not username.strip():
            return False, "Юзернейм не может быть пустым"
        
        clean_username = username.lstrip('@').strip()
        
        if len(clean_username) > 100:
            return False, "Юзернейм слишком длинный (максимум 100 символов)"
        
        if len(clean_username) < 2:
            return False, "Юзернейм слишком короткий (минимум 2 символа)"
        
        if not re.match(r'^[a-zA-Z0-9_\-\.]+$', clean_username):
            return False, "Юзернейм содержит недопустимые символы"
        
        return True, ""
    
    @staticmethod
    def sanitize_html(text: str) -> str:
        if not text:
            return ""
        
        replacements = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;'
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    @staticmethod
    def format_username(username: str) -> str:
        if not username:
            return ""
        
        username = username.strip()
        if username and not username.startswith('@'):
            return f"@{username}"
        
        return username


class RateLimiter:
    
    def __init__(self):
        self.user_requests = {}
    
    def check_rate_limit(self, user_id: int, max_requests: int = 5, time_window: int = 60) -> bool:
        import time
        
        current_time = time.time()
        
        if user_id not in self.user_requests:
            self.user_requests[user_id] = []
        
        self.user_requests[user_id] = [
            req_time for req_time in self.user_requests[user_id]
            if current_time - req_time < time_window
        ]
        
        if len(self.user_requests[user_id]) >= max_requests:
            return False
        
        self.user_requests[user_id].append(current_time)
        return True
