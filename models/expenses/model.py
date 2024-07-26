from typing import NamedTuple, Optional


class MessageModel(NamedTuple):
    amount: int
    category_text: str


class ExpenseModel(NamedTuple):
    id: Optional[int]
    amount: int
    category_name: str