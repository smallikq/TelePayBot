from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Payment:
    id: Optional[int] = None
    employee_id: int = 0
    employee_username: Optional[str] = None
    employee_first_name: Optional[str] = None
    balance: str = ""
    username_field: str = ""
    screenshot_file_id: str = ""
    status: str = "pending"
    payment_amount: Optional[int] = None
    replied: bool = False
    employee_message_id: Optional[int] = None
    created_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

