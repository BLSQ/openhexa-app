from decimal import Decimal


def format_cost(value: Decimal) -> str:
    """
    Transforms a cost in full dollars (or any currency) to a formatted readable string
    with maximum 4 decimals (e.g.: 1.0, 0.12, 0.1234)
    """
    formatted = f"{value:.4f}".rstrip("0")
    if formatted.endswith("."):
        formatted += "0"  # ensure at least one decimal
    return f"${formatted}"
