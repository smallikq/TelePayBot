"""
Unit tests for the TelePayBot
Run with: pytest tests/
"""
import pytest
import asyncio
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import Database
from models import Payment
from utils import Validator


class TestValidator:
    """Test cases for Validator class"""
    
    def test_validate_balance_valid(self):
        """Test valid balance formats"""
        is_valid, _ = Validator.validate_balance("100$")
        assert is_valid is True
        
        is_valid, _ = Validator.validate_balance("50")
        assert is_valid is True
        
        is_valid, _ = Validator.validate_balance("25.50 USD")
        assert is_valid is True
    
    def test_validate_balance_invalid(self):
        """Test invalid balance formats"""
        is_valid, error = Validator.validate_balance("")
        assert is_valid is False
        assert "пустым" in error.lower()
        
        is_valid, error = Validator.validate_balance("abc")
        assert is_valid is False
        
        is_valid, error = Validator.validate_balance("x" * 100)
        assert is_valid is False
        assert "длинный" in error.lower()
    
    def test_validate_username_valid(self):
        """Test valid username formats"""
        is_valid, _ = Validator.validate_username("@username")
        assert is_valid is True
        
        is_valid, _ = Validator.validate_username("username123")
        assert is_valid is True
        
        is_valid, _ = Validator.validate_username("user_name")
        assert is_valid is True
    
    def test_validate_username_invalid(self):
        """Test invalid username formats"""
        is_valid, error = Validator.validate_username("")
        assert is_valid is False
        
        is_valid, error = Validator.validate_username("a")
        assert is_valid is False
        assert "короткий" in error.lower()
        
        is_valid, error = Validator.validate_username("user@name!")
        assert is_valid is False
        assert "недопустимые" in error.lower()
    
    def test_sanitize_html(self):
        """Test HTML sanitization"""
        result = Validator.sanitize_html("<script>alert('xss')</script>")
        assert "<script>" not in result
        assert "&lt;script&gt;" in result
        
        result = Validator.sanitize_html("normal text")
        assert result == "normal text"
    
    def test_format_username(self):
        """Test username formatting"""
        assert Validator.format_username("username") == "@username"
        assert Validator.format_username("@username") == "@username"
        assert Validator.format_username("") == ""


class TestDatabase:
    """Test cases for Database class"""
    
    @pytest.fixture
    async def db(self):
        """Create a test database"""
        test_db = Database("test_bot.db")
        await test_db.init_db()
        yield test_db
        await test_db.close()
        # Cleanup
        if os.path.exists("test_bot.db"):
            os.remove("test_bot.db")
    
    @pytest.mark.asyncio
    async def test_create_payment(self, db):
        """Test creating a payment request"""
        payment = Payment(
            employee_id=12345,
            employee_username="testuser",
            balance="100$",
            username_field="@testaccount",
            screenshot_file_id="file_123"
        )
        
        payment_id = await db.create_payment(payment)
        assert payment_id > 0
    
    @pytest.mark.asyncio
    async def test_get_payment_by_id(self, db):
        """Test retrieving payment by ID"""
        # Create payment first
        payment = Payment(
            employee_id=12345,
            employee_username="testuser",
            balance="100$",
            username_field="@testaccount",
            screenshot_file_id="file_123"
        )
        payment_id = await db.create_payment(payment)
        
        # Retrieve it
        retrieved = await db.get_payment_by_id(payment_id)
        assert retrieved is not None
        assert retrieved.employee_id == 12345
        assert retrieved.balance == "100$"
        assert retrieved.status == "pending"
    
    @pytest.mark.asyncio
    async def test_get_user_pending_payments(self, db):
        """Test getting pending payments for a user"""
        # Create multiple payments
        for i in range(3):
            payment = Payment(
                employee_id=12345,
                employee_username="testuser",
                balance=f"{100 + i}$",
                username_field=f"@account{i}",
                screenshot_file_id=f"file_{i}"
            )
            await db.create_payment(payment)
        
        # Get pending payments
        payments = await db.get_user_pending_payments(12345)
        assert len(payments) == 3
    
    @pytest.mark.asyncio
    async def test_update_payment_status(self, db):
        """Test updating payment status"""
        # Create payment
        payment = Payment(
            employee_id=12345,
            employee_username="testuser",
            balance="100$",
            username_field="@testaccount",
            screenshot_file_id="file_123"
        )
        payment_id = await db.create_payment(payment)
        
        # Update status
        await db.update_payment_status(payment_id, "paid", 25)
        
        # Verify update
        updated = await db.get_payment_by_id(payment_id)
        assert updated.status == "paid"
        assert updated.payment_amount == 25
        assert updated.paid_at is not None
    
    @pytest.mark.asyncio
    async def test_delete_payment(self, db):
        """Test deleting a payment"""
        # Create payment
        payment = Payment(
            employee_id=12345,
            employee_username="testuser",
            balance="100$",
            username_field="@testaccount",
            screenshot_file_id="file_123"
        )
        payment_id = await db.create_payment(payment)
        
        # Delete it
        success = await db.delete_payment(payment_id, 12345)
        assert success is True
        
        # Verify deletion
        deleted = await db.get_payment_by_id(payment_id)
        assert deleted is None
    
    @pytest.mark.asyncio
    async def test_get_statistics(self, db):
        """Test getting payment statistics"""
        # Create and pay some payments
        for i in range(3):
            payment = Payment(
                employee_id=12345 + i,
                employee_username=f"user{i}",
                balance=f"{100}$",
                username_field=f"@account{i}",
                screenshot_file_id=f"file_{i}"
            )
            payment_id = await db.create_payment(payment)
            await db.update_payment_status(payment_id, "paid", 15 + i * 5)
        
        # Get statistics
        stats = await db.get_statistics(days=30)
        assert stats['total_paid'] == 3
        assert stats['total_amount'] > 0
        assert len(stats['by_employee']) == 3


class TestModels:
    """Test cases for data models"""
    
    def test_payment_creation(self):
        """Test Payment model creation"""
        payment = Payment(
            employee_id=12345,
            employee_username="testuser",
            balance="100$",
            username_field="@testaccount",
            screenshot_file_id="file_123"
        )
        
        assert payment.employee_id == 12345
        assert payment.status == "pending"
        assert payment.replied is False
        assert isinstance(payment.created_at, datetime)
    
    def test_payment_defaults(self):
        """Test Payment model default values"""
        payment = Payment()
        assert payment.employee_id == 0
        assert payment.status == "pending"
        assert payment.replied is False
        assert payment.created_at is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
