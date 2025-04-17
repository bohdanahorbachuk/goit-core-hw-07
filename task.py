from collections import UserDict
from datetime import datetime, timedelta
import re


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not re.fullmatch(r"\d{10}", value):
            raise ValueError("Номер телефону має містити рівно 10 цифр")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Невірний формат дати. Використовуйте DD.MM.YYYY")
        super().__init__(value)


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return
        raise ValueError("Телефон не знайдено")

    def edit_phone(self, old_phone, new_phone):
        for i, p in enumerate(self.phones):
            if p.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return
        raise ValueError("Старий телефон не знайдено")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, date_str):
        self.birthday = Birthday(date_str)

    def __str__(self):
        phones = "; ".join(str(p) for p in self.phones)
        birthday = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name}, phones: {phones}{birthday}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value.lower()] = record

    def find(self, name):
        return self.data.get(name.lower())

    def delete(self, name):
        self.data.pop(name.lower(), None)

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming = []
        for record in self.data.values():
            if record.birthday:
                bday = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                bday_this_year = bday.replace(year=today.year)
                if today <= bday_this_year <= today + timedelta(days=7):
                    if bday_this_year.weekday() >= 5:
                        bday_this_year += timedelta(days=7 - bday_this_year.weekday())
                    upcoming.append({"name": record.name.value, "birthday": bday_this_year.strftime("%d.%m.%Y")})
        return upcoming


def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return f"Error: {e}"
    return wrapper


@input_error
def add_contact(args, book):
    name, phone = args.split()
    record = book.find(name)
    if not record:
        record = Record(name)
        book.add_record(record)
        msg = "Contact added."
    else:
        msg = "Contact updated."
    record.add_phone(phone)
    return msg


@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args.split()
    record = book.find(name)
    if not record:
        raise ValueError("Contact not found.")
    record.edit_phone(old_phone, new_phone)
    return "Phone updated."


@input_error
def show_phones(args, book):
    record = book.find(args.strip())
    if not record:
        raise ValueError("Contact not found.")
    return "; ".join(p.value for p in record.phones)


@input_error
def add_birthday(args, book):
    name, date_str = args.split()
    record = book.find(name)
    if not record:
        raise ValueError("Contact not found.")
    record.add_birthday(date_str)
    return "Birthday added."


@input_error
def show_birthday(args, book):
    record = book.find(args.strip())
    if not record or not record.birthday:
        raise ValueError("Birthday not found.")
    return record.birthday.value


@input_error
def birthdays(_, book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays."
    return "\n".join(f"{b['name']}: {b['birthday']}" for b in upcoming)


def show_all(book):
    if not book.data:
        return "No contacts found."
    return "\n".join(str(record) for record in book.data.values())


def parse_input(user_input):
    return user_input.strip().split(maxsplit=1)


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ").strip()
        if not user_input:
            continue

        command, *rest = parse_input(user_input)
        args = rest[0] if rest else ""

        if command in ("exit", "close"):
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phones(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()