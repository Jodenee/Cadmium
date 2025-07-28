def spaced_print(message: str) -> None:
    print(f"{message}\n")


def spaced_input(input_message: str) -> str:
    user_input: str = input(input_message)
    print("\n")

    return user_input
