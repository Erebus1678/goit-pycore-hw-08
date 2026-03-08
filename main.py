import pickle
from functools import wraps
from typing import Tuple, List

from addressbook import AddressBook, Record


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


def input_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except KeyError as e:
            return str(e)
        except IndexError:
            return "Not enough arguments. Please check the command format."
    return wrapper


def parse_input(user_input: str) -> Tuple[str, List[str]]:
    user_input = user_input.strip()
    if not user_input:
        return "", []
    parts = user_input.split()
    command = parts[0].lower()
    args = parts[1:]
    return command, args


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    record.edit_phone(old_phone, new_phone)
    return "Phone number changed."


@input_error
def show_phone(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    if not record.phones:
        return f"{name}: no phones saved."
    return ", ".join(p.value for p in record.phones)


@input_error
def show_all(book: AddressBook):
    if not book.data:
        return "Address book is empty."
    lines = []
    for record in book.data.values():
        lines.append(str(record))
    return "\n".join(lines)


@input_error
def add_birthday(args, book: AddressBook):
    name, birthday, *_ = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    record.add_birthday(birthday)
    return "Birthday added."


@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    if record.birthday is None:
        return "Birthday is not set for this contact."
    return str(record.birthday)


@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays in the next 7 days."

    grouped = {}
    for item in upcoming:
        grouped.setdefault(item["congratulation_date"], []).append(item["name"])

    lines = []
    for d in sorted(grouped.keys(), key=lambda x: tuple(reversed(x.split(".")))):
        names = ", ".join(grouped[d])
        lines.append(f"{d}: {names}")
    return "\n".join(lines)


def main():
    book = load_data()

    handlers = {
        "": lambda current_args, current_book: "Please enter a command.",
        "hello": lambda current_args, current_book: "How can I help you?",
        "add": add_contact,
        "change": change_contact,
        "phone": show_phone,
        "all": lambda current_args, current_book: show_all(current_book),
        "add-birthday": add_birthday,
        "show-birthday": show_birthday,
        "birthdays": birthdays,
    }

    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break

        handler = handlers.get(command)
        if handler is None:
            print("Invalid command.")
            continue

        print(handler(args, book))


if __name__ == "__main__":
    main()