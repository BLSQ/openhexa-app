from decimal import Decimal


def format_cost(value: Decimal) -> str:
    formatted = f"{value:.4f}".rstrip("0")
    if formatted.endswith("."):
        formatted += "0"  # ensure at least one decimal
    return f"${formatted}"
