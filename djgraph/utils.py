def convert_snake_to_camel_case(snake: str):
    parts = snake.split("_")
    return "".join([x.capitalize() for x in parts])
