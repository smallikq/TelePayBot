"""Utility functions for the bot"""
import re
from typing import Tuple


class Validator:
    """Input validation utilities"""
    
    @staticmethod
    def validate_balance(balance: str) -> Tuple[bool, str]:
        """
        Validate balance format
        
        Args:
            balance: Balance string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not balance or not balance.strip():
            return False, "Баланс не может быть пустым"
        
        if len(balance) > 50:
            return False, "Баланс слишком длинный (максимум 50 символов)"
        
        # Check for basic format (should contain digits)
        if not any(char.isdigit() for char in balance):
            return False, "Баланс должен содержать числовое значение"
        
        return True, ""
    
    @staticmethod
    def validate_username(username: str) -> Tuple[bool, str]:
        """
        Validate username format
        
        Args:
            username: Username string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not username or not username.strip():
            return False, "Юзернейм не может быть пустым"
        
        # Remove @ if present
        clean_username = username.lstrip('@').strip()
        
        if len(clean_username) > 100:
            return False, "Юзернейм слишком длинный (максимум 100 символов)"
        
        if len(clean_username) < 2:
            return False, "Юзернейм слишком короткий (минимум 2 символа)"
        
        # Check for valid characters (alphanumeric, underscore, basic symbols)
        if not re.match(r'^[a-zA-Z0-9_\-\.]+$', clean_username):
            return False, "Юзернейм содержит недопустимые символы"
        
        return True, ""
    
    @staticmethod
    def sanitize_html(text: str) -> str:
        """
        Sanitize text for HTML output to prevent XSS
        
        Args:
            text: Text to sanitize
            
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        # Replace HTML special characters
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
        """
        Format username consistently
        
        Args:
            username: Username to format
            
        Returns:
            Formatted username with @ prefix if needed
        """
        if not username:
            return ""
        
        username = username.strip()
        if username and not username.startswith('@'):
            return f"@{username}"
        
        return username


class RateLimiter:
    """Simple rate limiter for preventing spam"""
    
    def __init__(self):
        self.user_requests = {}
    
    def check_rate_limit(self, user_id: int, max_requests: int = 5, time_window: int = 60) -> bool:
        """
        Check if user has exceeded rate limit
        
        Args:
            user_id: Telegram user ID
            max_requests: Maximum requests allowed
            time_window: Time window in seconds
            
        Returns:
            True if within rate limit, False if exceeded
        """
        import time
        
        current_time = time.time()
        
        if user_id not in self.user_requests:
            self.user_requests[user_id] = []
        
        # Remove old requests outside time window
        self.user_requests[user_id] = [
            req_time for req_time in self.user_requests[user_id]
            if current_time - req_time < time_window
        ]
        
        # Check if limit exceeded
        if len(self.user_requests[user_id]) >= max_requests:
            return False
        
        # Add current request
        self.user_requests[user_id].append(current_time)
        return True
