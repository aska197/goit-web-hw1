from abc import ABC, abstractmethod
from collections import UserDict
from datetime import datetime, timedelta
import pickle

class Field(ABC):
    @abstractmethod
    def display_info(self):
        pass

class InfoDisplay(ABC):
    @abstractmethod
    def display_all_users(self):
        pass

    @abstractmethod
    def display_help(self):
        pass

from abc import ABC, abstractmethod

class UserInterface(ABC):
    @abstractmethod
    def print_message(self, message):
        pass

    @abstractmethod
    def get_user_input(self):
        pass

class Name(Field):
    def __init__(self, value):
        self.value = value

    def display_info(self):
        return str(self.value)

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must contain 10 digits.")
        self.value = value

    def display_info(self):
        return str(self.value)
    
class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, '%d.%m.%Y')
        except ValueError:
            raise ValueError('Invalid date format. Use DD.MM.YYYY')

    def display_info(self):
        return self.value.strftime('%d.%m.%Y')

class AbstractRecord(ABC):
    @abstractmethod
    def add_phone(self, phone):
        pass

    @abstractmethod
    def add_birthday(self, birthday):
        pass

    @abstractmethod
    def remove_phone(self, phone):
        pass

    @abstractmethod
    def edit_phone(self, old_phone, new_phone):
        pass

    @abstractmethod
    def find_phone(self, phone):
        pass

    @abstractmethod
    def display_info(self):
        pass

class Record(AbstractRecord):
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        if not isinstance(phone, Phone):
            raise ValueError('Invalid phone value. Use Phone instance')
        self.phones.append(phone)

    def add_birthday(self, birthday):
        if not isinstance(birthday, Birthday):
            raise ValueError('Invalid birthday value. Use Birthday instance')
        self.birthday = birthday

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if str(p) != phone]

    def edit_phone(self, old_phone, new_phone):
        for i, p in enumerate(self.phones):
            if str(p) == old_phone:
                self.phones[i] = Phone(new_phone)
                return
        raise ValueError(f'Phone number {old_phone} not found for editing.')

    def find_phone(self, phone):
        for p in self.phones:
            if str(p) == phone:
                return p
        return None

    def display_info(self):
        phones_str = '; '.join(str(phone.value) for phone in self.phones)
        birthday_str = str(self.birthday.value.strftime('%d.%m.%Y')) if self.birthday else 'Not Set'
        return f"Contact name: {self.name.value}, phones: {phones_str}, birthday: {birthday_str}"

    def __str__(self):
        return self.display_info()

class AddressBook(UserDict, InfoDisplay):
    def __init__(self):
        super().__init__()

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday:
                birthday_date = record.birthday.value.date()

                birthday_this_year = birthday_date.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                days_until_birthday = (birthday_this_year - today).days

                if 0 <= days_until_birthday <= 7:

                    if birthday_this_year.weekday() in [5, 6]:
                        monday_after_birthday = birthday_this_year + timedelta(days=(7 - birthday_this_year.weekday()))
                        congradulation_date = monday_after_birthday.strftime('%d.%m.%Y')
                    else:
                        congradulation_date = birthday_this_year.strftime('%d.%m.%Y')

                    upcoming_birthdays.append({'name': record.name.value, 'congradulation_date': congradulation_date})

        return upcoming_birthdays

    def display_all_users(self):
        if self.data:
            print('All contacts:')
            for name, record in self.data.items():
                print(record)
        else:
            print('No contacts found.')

    def display_help(self):
        print('No help available for the address book.')

    def load_data(filename='addressbook.pk1'):
        try:
            with open(filename, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            return AddressBook()

class ConsoleInterface(UserInterface):
    def print_message(self, message):
        print(message)

    def get_user_input(self):
        return input('Enter a command: ')
    
    def display_help(self):
        print('List of available commands:')
        print('add [name] [phone number]: Add a new contact with the given name and phone number.')
        print('change phone [name] [new phone number]: Change the phone number for the contact with the given name.')
        print('phone [name]: Display the phone number for the contact with the given name.')
        print('all: Display information about all contacts.')
        print('add birthday [name] [birthday date]: Add a birthday for the contact with the given name.')
        print('show birthday [name]: Display the birthday for the contact with the given name.')
        print('birthdays: Display upcoming birthdays for the next week.')
        print('exit: Save data and exit the application.')


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, KeyError, IndexError) as e:
            error_messages = {
                KeyError: 'Contact not found.',
                ValueError: 'Invalid command format.',
                IndexError: 'Invalid command format.'
            }
            return error_messages.get(type(e), 'An error occured. Please try again.')
    return inner

def parse_input(user_input):
    parts = user_input.split(maxsplit=1)
    cmd = parts[0].strip().lower()
    args = parts[1].split() if len(parts) > 1 else []
    return cmd, args

# Handler function for adding a birthday to a contact
@input_error
def add_birthday(args, book):
    if len(args) != 2:
        print('Usage: add birthday [name] [birthdaydate]')
        return
    name, birthday = args
    try:
        record = book.find(name)
        if record:
            record.add_birthday(Birthday(birthday))
            print(f'Birthday added for {name}.')
        else:
            print(f'Contact {name} not found.')
    except ValueError as e:
        print(str(e))

# Handler function for displaying a contact's birthday
@input_error
def show_birthday(args, book):
    if len(args) != 1:
        print('Usage: show birthday [name]')
        return
    name = args[0]
    try:
        record = book.find(name)
        if record:
            if record.birthday:
                print(f'{name} birthday is on {record.birthday.value.strftime("%d.%m.%Y")}.')
            else:
                print(f'No birthday set for {name}.')
        else:
            print(f'Contact {name} not found.')
    except ValueError as e:
        print(str(e))

# Handler function to display birthdays in the next week
@input_error
def birthdays(args, book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if upcoming_birthdays:
        print(f'Upcoming birthdays for next week:')
        for contact in upcoming_birthdays:
            print(f"{contact['name']} birthday is on {contact['congradulation_date']}.")
    else:
        print('No upcoming birthdays for next week.')

# Handler function for changing phone number for a contact
@input_error
def change_phone(args, book):
    if len(args) != 2:
        print('Usage: change phone [name] [new phone number]')
        return
    name, new_phone = args
    try:
        record = book.find(name)
        if record:
            old_phone = str(record.phones[0])
            record.edit_phone(old_phone, Phone(new_phone))
            print(f'Phone number for {name} changed from {old_phone} to {new_phone}.')
        else: 
            print(f'Contact {name} not found.')
    except ValueError as e:
        print(str(e))

def handle_hello_command():
    print('How can I help you')

def handle_add_command(args, book):
    if len(args) != 2:
        print('Usage: add [name] [phone number]')
        return
    name, phone = args
    try:
        record = Record(name)
        record.add_phone(Phone(phone))
        book.add_record(record)
        print(f'Contact {name} with phone {phone} added.')
    except ValueError as e:
        print(str(e))

def handle_change_phone_command(args, book):
    if len(args) != 2:
        print('Usage: change phone [name] [new phone number]')
        return
    name, new_phone = args
    try:
        record = book.find(name)
        if record:
            old_phone = str(record.phones[0])
            record.edit_phone(old_phone, Phone(new_phone))
            print(f'Phone number for {name} changed from {old_phone} to {new_phone}.')
        else:
            print(f'Contact {name} not found.')
    except ValueError as e:
        print(str(e))

def handle_phone_command(args, book):
    if len(args) != 1:
        print('Usage: phone [name]')
        return
    name = args[0]
    try:
        record = book.find(name)
        if record:
            if record.phones:
                print(f'Phone number for {name}: {record.phones[0]}')
            else:
                print(f'No phone number found for {name}.')
        else:
            print(f'Contact {name} not found.')
    except ValueError as e:
        print(str(e))

def handle_all_command(book):
    book.display_all_users()

def save_data(book, filename='addressbook.pk1'):
    with open(filename, 'wb') as f:
        pickle.dump(book, f)

def load_data(filename='addressbook.pk1'):
    try:
        with open(filename, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

class Application:
    def __init__(self, ui):
        self.ui = ui
        self.book = load_data()

    def run(self):
        self.ui.print_message('Welcome to the assistant bot!')
        while True:
            user_input = self.ui.get_user_input()
            command, args = parse_input(user_input)

            if command in ['close', 'exit']:
                self.ui.print_message('Good bye!')
                save_data(self.book)
                break

            elif command == 'hello':
                handle_hello_command()

            elif command == 'add':
                if args and args[0] == 'birthday':
                    add_birthday(args[1:], self.book)
                else:
                    handle_add_command(args, self.book)

            elif command == 'change phone':
                handle_change_phone_command(args, self.book)

            elif command == 'phone':
                handle_phone_command(args, self.book)

            elif command == 'all':
                handle_all_command(self.book)

            elif command == 'add birthday':
                add_birthday(args, self.book)

            elif command == 'show birthday':
                show_birthday(args, self.book)

            elif command == 'birthdays':
                birthdays(args, self.book)

            elif command == 'help':
                self.ui.display_help()

            else:
                self.ui.print_message('Invalid command.')

if __name__ == '__main__':
    ui = ConsoleInterface()
    app = Application(ui)
    app.run()
       
