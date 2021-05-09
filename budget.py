from __future__ import annotations

import math
from functools import reduce
from operator import add
from typing import Any, Dict, List, Union


# Data Types.
Number = Union[int, float]


class Category:
    """The Category class."""
    def __init__(self, category_name: str):
        self.category_name: str = category_name
        self.ledger: List[Dict[str, Any]] = []

    def __str__(self) -> str:
        """Returns a string representation of the instance."""
        def format_header(name: str) -> str:
            left_star_multiplier: int = int((30 - len(name)) / 2)
            right_star_multiplier: int = int(30 - len(name) - left_star_multiplier)
            return f"{'*' * left_star_multiplier}{name}{'*' * right_star_multiplier}"

        def format_ledger_entry(entry: Dict[str, Any]) -> str:
            description: str = entry.get("description")[:23]
            amount: str = f"{entry.get('amount'):.2f}"
            space_multiplier: int = 30 - len(amount) - len(description)
            return f"{description}{' ' * space_multiplier}{amount}"

        def format_total(amount: str) -> str:
            return f"Total: {amount}"

        result: str = f"{format_header(self.category_name)}\n"
        for entry in self.ledger:
            result += f"{format_ledger_entry(entry)}\n"
        result += format_total(self.get_balance())
        return result

    def check_funds(self, amount: Number) -> bool:
        """Returns if `amount` is less than or equal balance."""
        return amount <= self.get_balance()
    
    def deposit(self, amount: Number, description: str = "") -> None:
        """Records a deposit event in the ledger."""
        self.ledger.append({"amount": amount, "description": description})

    def get_balance(self) -> Number:
        """Returns the income - withdraw values in the ledger."""
        return reduce(add, [i.get("amount") for i in self.ledger])

    def withdraw(self, amount: Number, description: str = "") -> bool:
        """Records a withdraw event in the ledger.

        :return: True when event successful
        """
        result: bool = False
        if self.check_funds(amount):
            self.ledger.append({"amount": amount * -1, "description": description})
            result = True
        return result

    def transfer(self, amount: Number, category: Category) -> bool:
        """Records a transfer event in category ledgers.

        :return: True when event successful
        """
        result: bool = False
        if self.withdraw(amount, f"Transfer to {category.category_name}"):
            category.deposit(amount, f"Transfer from {self.category_name}")
            result = True
        return result


def create_spend_chart(categories):
    # Resolve the maximum length of a category name.
    y_length: int = reduce(max, [len(i.category_name) for i in categories])
    # Calculate the withdraw total for each category.
    # This is represented as a list i.e. [23.5, 56.89, 10.00]
    category_withdraw: list = list(map(_calculate_category_withdraw, categories))
    # Find the total of withdraw across all categories.
    total_withdraw: int = int(reduce(add, category_withdraw, 0.0))
    # Calculate the percentage of the total withdraw for each category.
    # Note: at this stage the percentages are rounded down to the nearest 10.
    # This is represented as a list i.e. [30, 60, 10]
    withdraw_percents: list = list(
        map(_resolve_percentage, category_withdraw, [total_withdraw] * len(category_withdraw))
    )

    # Build the 2D list to represent the graph.

    # Here we're going to use a 2D list to represent the graph where each index
    # represents a character space in the graph.
    # Imagine drawing the graph on squared paper...
    # The *outer* list is the x-axis with each index referencing another list that
    # represents the y-axis.
    # The first 5 x-axis lists represent the y-axis labels and a blank column.
    # Then for each column, we're compiling a content column followed by 2 blank columns.
    string_list: list = _format_y_labels(y_length)
    string_list.extend(_format_blank_columm(y_length))
    # Compile a column for each category then add 2 blank columns after it.
    for index, category in enumerate(categories):
        string_list.extend(_format_category_column(y_length, category.category_name, withdraw_percents[index]))

    # Build the output string.

    # Convert the 2D list into a string with a nested for-loop.
    # The first round adds [0][0], [1][0], [2][0], etc.
    # Here we're moving along each sub-list adding it's value at index 0 then
    # we'll move along each sub-list adding it's value at index 1 and so on.
    # To visualise this, let's look at the 2D list in a different way;
    #   0    1    2
    # [[0], [0], [0], ..]
    #  [1], [1], [1],
    #   ..,  ..,  ..,
    ret_val: str = "Percentage spent by category\n"
    for i in range(y_length + 12):
        for j in range(len(string_list)):
            ret_val += string_list[j][i]
        ret_val += "\n"
    # Given the nature of our list -> string conversion, we'll need to remove
    # redundant trailing whitespace and add a double space.
    return ret_val.rstrip() + "  "


def _calculate_category_withdraw(category: Category) -> float:
    """Return total withdraw amount for `category`."""
    withdraw: float = 0.0
    for entry in category.ledger:
        amount: Number = entry.get("amount")
        if amount < 0:
            withdraw += amount * -1
    return withdraw


def _resolve_percentage(value: Number, total: Number) -> int:
    """Return rounded percentage `value` is of `total`."""
    percentage: int = int(value / total * 100)
    return _round_down_nearest_ten(percentage)


def _round_down_nearest_ten(value: int) -> int:
    """Round value down to the nearest 10.

    :note: Adapted from https://realpython.com/python-rounding/#rounding-down
    """
    return int(math.floor(value * 0.1) / 0.1)


def _format_y_labels(longest_category_name: int) -> list:
    """Returns string arrays of y-axis labels."""
    return [
        ["1"] + [" "] * (11 + longest_category_name),
        ["0", "9", "8", "7", "6", "5", "4", "3", "2", "1", " ", " "] + [" "] * longest_category_name,
        ["0"] * 11 + [" "] * (1 + longest_category_name),
        ["|"] * 11 + [" "] * (1 + longest_category_name)
    ]


def _format_blank_columm(longest_category_name: int) -> list:
    """Returns string array of a blank column."""
    return [
        [" "] * 11 + ["-"] + [" "] * longest_category_name
    ]


def _format_category_column(longest_category_name: int, category_name: str, category_percentage: int) -> list:
    """Returns string arrays of content column with 2 blank columns."""
    top_fillers: list = [" "] * int(10 - category_percentage / 10)
    o_fillers: list = ["o"] * int(category_percentage / 10 + 1)
    bottom_fillers: list = [" "] * int(longest_category_name - len(category_name))
    category_column: list =[
        top_fillers + o_fillers + ["-"] + list(category_name) + bottom_fillers,
    ]
    category_column.extend(_format_blank_columm(longest_category_name))
    category_column.extend(_format_blank_columm(longest_category_name))
    return category_column
