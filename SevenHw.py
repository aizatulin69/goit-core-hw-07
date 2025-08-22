from collections import UserDict
from datetime import datetime, date, timedelta



class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not (value.isdigit() and len(value) == 10):
            raise ValueError("Invalid phone format. Use 10 digits")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value: str):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)


class Record:
    def __init__(self, name: str, phones=None, birthday=None):
        self.name = Name(name)
        self.phones = [Phone(p) for p in (phones or [])]
        self.birthday = Birthday(birthday) if birthday else None

    def add_contact(self, phone: str):
        p = Phone(phone)
        self.phones.append(p)
        return p

    def change_phone(self, old_phone: str, new_phone: str):
        phone_obj = self.find_phone(old_phone)
        if not phone_obj:
            raise ValueError(f"Phone {old_phone} not found")
        self.phones.remove(phone_obj)
        p = Phone(new_phone)
        self.phones.append(p)
        return p

    def remove_phone(self, phone: str):
        phone_obj = self.find_phone(phone)
        if not phone_obj:
            raise ValueError(f"Phone {phone} not found")
        self.phones.remove(phone_obj)
        return phone_obj

    def find_phone(self, phone: str):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday: str):
        b = Birthday(birthday)
        self.birthday = b
        return b

    def show_birthday(self):
        return self.birthday

    def __str__(self):
        phones = ", ".join(p.value for p in self.phones) if self.phones else "no phones"
        bday = f", Birthday: {self.birthday.value}" if self.birthday else ""
        return f"{self.name.value}: {phones}{bday}"

class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record
        return record

    def get_record(self, name: str):
        return self.data.get(name)



def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IndexError:
            return "Enter correct command"
        except ValueError as e:
            return str(e)
        except KeyError as e:
            return str(e)
        except AttributeError:
            return "Wrong input"
    return wrapper


def check_args(min_args: int):
    def decorator(func):
        def wrapper(book, args, *f_args, **f_kwargs):
            if len(args) < min_args:
                raise ValueError(f"Not enough arguments. Expected at least {min_args}")
            return func(book, args, *f_args, **f_kwargs)
        return wrapper
    return decorator


def parse_input(command: str):
    if not command.strip():
        return None, []
    parts = command.strip().split()
    return parts[0].lower(), parts[1:]


@input_error
@check_args(1)
def add_contact(book: AddressBook, args):
    if not args:
        raise ValueError("You must provide a name")
    name, *phones = args
    record = book.get_record(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    for phone in phones:
        record.add_contact(phone)
    return message


@input_error
@check_args(3)
def change_contact(book: AddressBook, args):
    name, old_phone, new_phone = args
    record = book.get_record(name)
    if not record:
        raise KeyError(f"No such contact: {name}")
    record.change_phone(old_phone, new_phone)
    return f"Phone changed for {name}"


@input_error
@check_args(1)
def show_phone(book: AddressBook, args):
    name = args[0]
    record = book.get_record(name)
    if not record:
        raise KeyError(f"No such contact: {name}")
    return ", ".join(p.value for p in record.phones) or "No phones"


@input_error
@check_args(2)
def add_birthday(book: AddressBook, args):
    name, birthday = args
    record = book.get_record(name)
    if not record:
        raise KeyError(f"No such contact: {name}")
    record.add_birthday(birthday)
    return f"Birthday {birthday} added for {name}"


@input_error
@check_args(1)
def show_birthday(book: AddressBook, args):
    name = args[0]
    record = book.get_record(name)
    if not record or not record.birthday:
        return f"No birthday set for {name}"
    return f"{name}'s birthday is {record.birthday.value}"


def get_upcoming_birthdays(book: AddressBook, days=7):
    upcoming_birthdays = []
    today = date.today()

    for record in book.data.values():
        if record.birthday:
            birthday = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
            birthday_this_year = birthday.replace(year=today.year)

            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)

            days_diff = (birthday_this_year - today).days
            if 0 <= days_diff < days:
                if birthday_this_year.weekday() in (5, 6):
                    birthday_this_year += timedelta(days=(7 - birthday_this_year.weekday()))
                upcoming_birthdays.append({
                    "name": record.name.value,
                    "birthday": birthday_this_year.strftime("%d.%m.%Y"),
                })
    return upcoming_birthdays


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input(">>> ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(book, args))
        elif command == "change":
            print(change_contact(book, args))
        elif command == "phone":
            print(show_phone(book, args))
        elif command == "add-birthday":
            print(add_birthday(book, args))
        elif command == "show-birthday":
            print(show_birthday(book, args))
        elif command == "birthdays":
            upcoming = get_upcoming_birthdays(book)
            if upcoming:
                for u in upcoming:
                    print(f"{u['name']} -> {u['birthday']}")
            else:
                print("No upcoming birthdays")
        elif command == "all":
            print("\n".join(str(r) for r in book.data.values()) or "Address book is empty")
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()

