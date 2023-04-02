import os
import sys
from core import execute


def user_input() -> str:
    return input("Enter your instruction: ")


def main():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: API_KEY environment variable not set.")
        sys.exit(1)

    history = []

    while True:
        task = user_input()
        if task.lower() == "exit":
            break

        history = execute(task, api_key, print, history)
        print()

if __name__ == "__main__":
    main()
