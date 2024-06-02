from collections import UserDict
from datetime import datetime, date
import pickle


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Name is a mandatory field")
        super().__init__(value)


class Phone(Field):
    def __init__(self, value):
        if not self.is_valid(value):
            raise ValueError("Phone number must be 10 digits")
        super().__init__(value)

    def is_valid(self, phone):
        return len(phone) == 10 and phone.isdigit()


class Birthday(Field):
    def __init__(self, value):
        super().__init__(value)
        try:
            self.value = datetime.strptime(value, '%d.%m.%Y').date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def __str__(self):
        return self.value.strftime('%d.%m.%Y')


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        for i, p in enumerate(self.phones):
            if p.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones_str = ', '.join(str(p) for p in self.phones)
        return f"Contact name: {self.name}, phones: {phones_str}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def find(self, name):
        return self.data.get(name)

    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays = []
        today = date.today()

        for record in self.data.values():
            if record.birthday:
                birthday_this_year = record.birthday.value.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                if 0 <= (birthday_this_year - today).days <= days:
                    congratulation_date_str = birthday_this_year.strftime('%Y-%m-%d')
                    upcoming_birthdays.append(
                        {"name": record.name.value, "congratulation_date": congratulation_date_str})

        return upcoming_birthdays

    def __str__(self):
        return '\n'.join(str(record) for record in self.data.values())


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except KeyError:
            return "Key Error"
        except IndexError:
            return "Please enter the name."

    return inner


@input_error
def delete_contact(args, book: AddressBook):
    if len(args) > 1:
        return "Give me only name."
    name = args[0]
    message = f"{name} successfully deleted"
    if name in book:
        book.delete(name)
    else:
        message = f"There are no {name} in your contacts"
    return message


@input_error
def add_contact(args, book: AddressBook):
    if len(args) < 2:
        return "Give me name and phone please."
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    else:
        for p in record.phones:
            if p.value == phone:
                return f"{name} already has this phone number."
    try:
        record.add_phone(phone)
    except ValueError as e:
        return str(e)
    return message


@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    if name in book:
        return book.find(name)
    else:
        return f"There are no {name} in your contacts"


@input_error
def change_contact(args, book: AddressBook):
    if len(args) < 3:
        return "Give me name, old phone number, and new phone number please."
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        for phone in record.phones:
            if phone.value == old_phone:
                record.phones.remove_phone(phone)
                record.add_phone(new_phone)
                return "Contact updated."
        return f"The contact {name} does not have the phone number {old_phone}."
    else:
        return f"There are no contacts with the name {name}. Type 'add' to add a new contact."


@input_error
def add_birthday(args, book: AddressBook):
    if len(args) < 2:
        return "Give me name and birthday please."
    name, birthday = args
    record = book.find(name)
    if record:
        try:
            record.add_birthday(birthday)
            return "Birthday added."
        except ValueError as e:
            return str(e)
    else:
        return f"There are no {name} in your contacts."


@input_error
def show_birthday(args, book: AddressBook):
    if len(args) < 1:
        return "Please provide a name."
    name = args[0]
    record = book.find(name)
    if record:
        if record.birthday:
            return f"Birthday for {name} is {record.birthday}."
        else:
            return f"No birthday set for {name}."
    else:
        return f"There are no contacts with the name {name}."


def show_all_contacts(book: AddressBook):
    return str(book) if book else "No contacts found."


def show_upcoming_birthdays(book: AddressBook):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return "No upcoming birthdays within the next week."
    result = "Upcoming birthdays:\n"
    for birthday in upcoming_birthdays:
        result += f"{birthday['name']}: {birthday['congratulation_date']}\n"
    return result


def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)
        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "delete":
            print(delete_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all_contacts(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(show_upcoming_birthdays(book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
