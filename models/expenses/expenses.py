""" Работа с расходами — их добавление, удаление, статистики"""
import datetime
import re
from typing import List

import pytz

import exceptions
from database.sqlite import SQLite
from models.categories import Categories
from models.expenses.model import ExpenseModel, MessageModel


class Expense:
    def __init__(self, db: SQLite):
        self.db = db

    def add_expense(self, raw_message: str) -> ExpenseModel:
        parsed_message = self._parse_message(raw_message)
        category = Categories().get_category(parsed_message.category_text)

        return ExpenseModel(id=None,
                       amount=parsed_message.amount,
                       category_name=category.name)


    def get_today_statistics(self) -> str:
        cursor = self.db.get_cursor()
        cursor.execute("select sum(amount)"
                       "from expense where date(created)=date('now', 'localtime')")
        result = cursor.fetchone()
        if not result[0]:
            return "Сегодня ещё нет расходов"
        all_today_expenses = result[0]
        cursor.execute("select sum(amount) "
                       "from expense where date(created)=date('now', 'localtime') "
                       "and category_codename in (select codename "
                       "from category where is_base_expense=true)")
        result = cursor.fetchone()
        base_today_expenses = result[0] if result[0] else 0
        return (f"Расходы сегодня:\n"
                f"всего — {all_today_expenses} руб.\n"
                f"базовые — {base_today_expenses} руб. из {self._get_budget_limit()} руб.\n\n"
                f"За текущий месяц: /month")


    def get_month_statistics(self) -> str:
        now = self._get_now_datetime()
        first_day_of_month = f'{now.year:04d}-{now.month:02d}-01'
        cursor = self.db.get_cursor()
        cursor.execute(f"select sum(amount) "
                       f"from expense where date(created) >= '{first_day_of_month}'")
        result = cursor.fetchone()
        if not result[0]:
            return "В этом месяце ещё нет расходов"
        all_today_expenses = result[0]
        cursor.execute(f"select sum(amount) "
                       f"from expense where date(created) >= '{first_day_of_month}' "
                       f"and category_codename in (select codename "
                       f"from category where is_base_expense=true)")
        result = cursor.fetchone()
        base_today_expenses = result[0] if result[0] else 0
        return (f"Расходы в текущем месяце:\n"
                f"всего — {all_today_expenses} руб.\n"
                f"базовые — {base_today_expenses} руб. из "
                f"{now.day * self._get_budget_limit()} руб.")


    def last(self) -> List[ExpenseModel]:
        cursor = self.db.get_cursor()
        cursor.execute(
            "select e.id, e.amount, c.name "
            "from expense e left join category c "
            "on c.codename=e.category_codename "
            "order by created desc limit 10")

        rows = cursor.fetchall()

        last_expenses = [ExpenseModel(id=row[0], amount=row[1], category_name=row[2]) for row in rows]
        return last_expenses


    def delete_expense(self, row_id: int) -> None:
        self.db.delete("expense", self.row_id)


    def _parse_message(self, raw_message: str) -> MessageModel:
        regexp_result = re.match(r"([\d ]+) (.*)", raw_message)
        if not regexp_result or not regexp_result.group(0) \
                or not regexp_result.group(1) or not regexp_result.group(2):
            raise exceptions.NotCorrectMessage(
                "Не могу понять сообщение. Напишите сообщение в формате, "
                "например:\n1500 метро")

        amount = regexp_result.group(1).replace(" ", "")
        category_text = regexp_result.group(2).strip().lower()
        return MessageModel(amount=amount, category_text=category_text)


    def _get_now_formatted(self) -> str:
        return self._get_now_datetime().strftime("%Y-%m-%d %H:%M:%S")


    @staticmethod
    def _get_now_datetime() -> datetime.datetime:
        tz = pytz.timezone("Europe/Moscow")
        now = datetime.datetime.now(tz)

        return now


    def _get_budget_limit(self) -> int:
        return self.db.fetchall("budget", ["daily_limit"])[0]["daily_limit"]
