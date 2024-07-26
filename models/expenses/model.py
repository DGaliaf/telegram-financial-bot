from typing import NamedTuple, Optional


class Message(NamedTuple):
    amount: int
    category_text: str


class Expense(NamedTuple):
    id: Optional[int]
    amount: int
    category_name: str