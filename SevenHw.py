from collections import UserDict
from datetime import datetime, date, timedelta


def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IndexError:
            return "Enter correct command"
        except ValueError as e:
            if "not enough values to unpack" in str(e):
                return "Not enough arguments provided"
            return str(e) or "Give me valid data"
        except KeyError as e:
            return str(e) or "No such contact"
        except AttributeError:
            return "Wrong input"

    return wrapper


@input_error
def parse_input(command):
    if not command.strip():
        raise ValueError("Empty input")
    parts = command.strip().split()
    action = parts[0].lower()
    args = parts[1:]
    return action, args


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
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format or date. Use DD.MM.YYYY")

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")


class Record:
    def __init__(self, name, phones=None):
        self.name = Name(name)
        self.phones = [Phone(p) for p in (phones or [])]
        self.birthday = None

    @input_error
    def add_phone(self, phone):
        self.phones.append(Phone(phone))
        return f"Phone {phone} added"

    @input_error
    def edit_phone(self, old_phone, new_phone):
        phone = self.find_phone(old_phone)
        if not phone:
            raise ValueError(f"Phone {old_phone} not found")
        self.remove_phone(old_phone)
        self.phones.append(Phone(new_phone))
        return f"Phone changed from {old_phone} to {new_phone}"

    @input_error
    def add_birthday(self, date_str):
        self.birthday = Birthday(date_str)
        if not self.birthday:
            return f"No birthday set for {self.name.value}"
        return f"Birthday {date_str} added for {self.name.value}"

    @input_error
    def show_birthday(self):
        if not self.birthday:
            return f"No birthday set for {self.name.value}"
        return f"{self.name.value}'s birthday is {self.birthday}"

    def remove_phone(self, phone):
        phone_obj = self.find_phone(phone)
        if not phone_obj:
            raise ValueError(f"Phone {phone} not found")
        self.phones.remove(phone_obj)

    def find_phone(self, phone_value):
        for phone in self.phones:
            if phone.value == phone_value:
                return phone
        return None

    def __str__(self):
        phones = ", ".join(p.value for p in self.phones) if self.phones else "no phones"
        birthday = f", Birthday: {self.birthday}" if self.birthday else ""
        return f"{self.name.value}: {phones}{birthday}"


class AddressBook(UserDict):

    @input_error
    def add_contact(self, args):
        name, *phones = args
        if name in self.data:
            record = self.data[name]
        else:
            record = Record(name)
            self.data[name] = record
        valid_phones = [Phone(p) for p in phones]
        for phone in valid_phones:
            record.phones.append(phone)
        return f"Contact {name} added/updated with {len(valid_phones)} phone(s)."
    
    @input_error
    def edit_phone(self, args):
        name, old_phone, new_phone = args
        record = self.data.get(name)
        if not record:
            raise KeyError(f"No such contact: {name}")
        return record.edit_phone(old_phone, new_phone)

    @input_error
    def add_birthday(self, args):
        name, birthday = args
        record = self.data[name]
        return record.add_birthday(birthday)

    @input_error
    def show_phones(self, args):
        name = args[0]
        record = self.data.get(name)
        if not record:
            raise KeyError(f"No such contact: {name}")
        return ", ".join(p.value for p in record.phones) or "No phones"

    @input_error
    def show_birthday(self, args):
        name = args[0]
        record = self.data.get(name)
        return record.show_birthday()

    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays = []
        today = date.today()

        for record in self.data.values():
            if record.birthday:
                birthday = record.birthday.value
                birthday_this_year = birthday.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(
                        year=today.year + 1
                    )

                days_diff = (birthday_this_year - today).days
                if 0 <= days_diff < days:
                    if birthday_this_year.weekday() in (5, 6):
                        birthday_this_year += timedelta(
                            days=(7 - birthday_this_year.weekday())
                        )
                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "birthday": birthday_this_year.strftime("%d.%m.%Y"),
                    })
        return upcoming_birthdays

    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())


@input_error
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
            print(book.add_contact(args))

        elif command == "change":
            print(book.edit_phone(args))

        elif command == "phone":
            print(book.show_phones(args))

        elif command == "add-birthday":
            print(book.add_birthday(args))

        elif command == "show-birthday":
            print(book.show_birthday(args))

        elif command == "birthdays":
            upcoming = book.get_upcoming_birthdays()
            if upcoming:
                for u in upcoming:
                    print(f"{u['name']} -> {u['birthday']}")
            else:
                print("No upcoming birthdays")

        elif command == "all":
            print(book if book.data else "Address book is empty")

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()


