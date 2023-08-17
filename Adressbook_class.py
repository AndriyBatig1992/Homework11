# #АДРЕСНА КНИГА

from collections import UserDict
from datetime import datetime, timedelta
import calendar
import re

class AddressBook(UserDict):
    def add_record(self, record):
        if self.validate_record(record):
            key = record.name.value
            self.data[key] = record
        else:
            print("Не вдалося додати запис, оскільки дані не валідні.")


    def remove_record(self, name):
        if name in self.data:
            del self.data[name]

    def find_records(self, **search_criteria):
        result = []
        for record in self.data.values():
            name_match = search_criteria.get('name') is None or record.name.value == search_criteria['name']
            phones_match = search_criteria.get('phones') is None or any(
                phone.getter_value == search_criteria['phones'] for phone in record.phones)
            if name_match and phones_match:
                result.append(record)
        return result

    def validate_record(self, record):
        valid_phones = all(isinstance(phone, Phone) and phone.validate(phone.value) for phone in record.phones)
        valid_name = isinstance(record.name, Name)
        valid_birthday = isinstance(record.birthday, Birthday) and record.birthday.validate(record.birthday.value)

        return valid_phones and valid_name and valid_birthday

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index < len(self.data):
            record = list(self.data.values())[self.index]
            self.index += 1
            return record
        else:
            raise StopIteration

    def iterator(self, n):
        return (list(self.data.values())[i:i + n] for i in range(0, len(self.data), n))


    def __str__(self):
        book_str = "\n".join(f"{name}: {record}" for name, record in self.data.items())
        return book_str


class Record:
    def __init__(self, name, phone=None, birthday=None):
        self.birthday = None if birthday is None else Birthday(birthday)
        self.name = Name(name)
        self.phones = [Phone(phone)] if phone is not None else []

    def add_phone_number(self, number):
        phone = Phone(number)
        if phone.validate(number):
            self.phones.append(phone)
        else:
            return False


    def remove_phone_number(self, number):
        if any(phone.value == number for phone in self.phones):
            new_phones = [phone for phone in self.phones if phone.value != number]
            self.phones = new_phones
            return True
        return False

    def change_phone_number(self, number, new_number):
        for index, phone in enumerate(self.phones):
            if phone.value == number:
                self.phones[index] = Phone(new_number)
                return True
        return False

    def days_to_birthday(self):
        if self.birthday and self.birthday.validate(self.birthday.value):
            parsed_date = datetime.strptime(self.birthday.value, '%d.%m.%Y').date()
            date_now = datetime.now().date()
            date_now_year = date_now.year
            next_year = date_now.year + 1
            parsed_date = parsed_date.replace(year=date_now_year)

            if parsed_date <= date_now:
                if calendar.isleap(next_year):
                    time_delta = (parsed_date - date_now + timedelta(days=366)).days
                else:
                    time_delta = (parsed_date - date_now + timedelta(days=365)).days
            else:
                time_delta = (parsed_date - date_now).days
            return time_delta
        else:
            return None


    def __str__(self):
        phones_str = ', '.join(str(phone) for phone in self.phones)
        return f"Name: {self.name.value}, Phones: {phones_str}"

class Field:
    def __init__(self, value):
        self.__value = None
        self.value=value

    def validate(self, new_value):
        return True
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, new_value):
        self.__value = new_value


    def __str__(self):
        return str(self.value)


class Phone(Field):
    def __init__(self, value=None):
        super().__init__(value)

    @Field.value.setter
    def value(self, new_value):
        if self.validate(new_value):
            Field.value.fset(self, new_value)
        else:
            print(f'Номер телефону {new_value} не можна призначити, оскільки він не валідний')

    def validate(self, number):
        if number is None:
            return False
        try:
            phone_format = r'\+380\d{9}'
            if not re.match(phone_format, number):
                return False
            return True
        except ValueError:
            return False


class Name(Field):
    def __init__(self, value):
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value=None):
        super().__init__(value)

    @Field.value.setter
    def value(self, new_value):
        if self.validate(new_value):
            Field.value.fset(self, new_value)
        else:
            print(f'Дату дня народження {new_value} не можна призначити, оскільки вона не валідна')

    def validate(self, new_value):
        try:
            datetime.strptime(new_value, '%d.%m.%Y').date()
            return True
        except ValueError:
            return False
        except TypeError:
            return False


if __name__=="__main__":

    # Перевірка
    # Створення об'єкта класу Record
    record = Record("Andriy Batig", "+380951234567", "01.01.1992")
    print(record.name)
    print(record.birthday)
    print(' '.join([f'Телефон: {phone}' for phone in record.phones]))

    #Використання методу додавання телефону
    record.add_phone_number("+380661234567")
    print(', '.join([
        f'Телефон: {phone}' if phone != record.phones[-1]
        else f'Новий телефон: {phone}' for phone in record.phones]))

    # Використання методу видалення телефону
    record.remove_phone_number("+380951234567")
    print(' '.join([f'Телефон, який залишився після видалення: {phone}' for phone in
                    record.phones]) if len(record.phones) == 1
else 'Телефони:' + ', '.join([f'{phone}' for phone in record.phones]))

    # Використання методу зміни телефону
    record.change_phone_number("+380661234567", "+380881234567")
    print(' '.join([f'Телефон, на який змінився старий телефон: {phone}' for phone in
                    record.phones]) if len(record.phones) == 1
          else 'Телефони:' + ', '.join([f'{phone}' for phone in record.phones]))

    # Перевірка методу days_to_birthday
    days = record.days_to_birthday()
    print(f'Днів до дня народження - {days}')

    # Створення об'єкту класу Birthday
    birthday = Birthday('01.10.2023')
    # Присвоєння валідної дати народження
    birthday.getter_value = '11.10.2022'
    print(f'Присвоєно нову дату народження через getter_value: {birthday.getter_value}')
    # Присвоєння не валідної дати народження з помилкою у форматі
    # birthday.getter_value = '01/10.2022'
    # Створення об'єкту класу Birthday з помилкою у форматі дати
    birthday1 = Birthday('01//10.2022')


    # Створення об'єкту класу Phone
    phone = Phone('+380503456787')
    # Присвоєння нового телефону через getter_value з помилкою у форматі
    phone.getter_value = '++380603456787'
    # Присвоєння валідного номера
    phone.getter_value = '+380123456787'
    print(f'Присвоєння валідного номеру телефону через getter_value: {phone.getter_value}')
    # Створення об'єкту класу Phone з неправильним форматом
    phone1 = Phone("++380503456787")

    #Cтворення об'єкта класу AddressBook
    book = AddressBook()
    # Cтворення об'єктів класу Record
    record1 = Record("Ivan", "+380503456787", "10.02.2003")
    record2 = Record("Pavlo", "+3805034567870", "12.02.2004")
    record3 = Record("Jhon", "++380503456787", "/11.02.1992")

    # Виклик методу add_record класу AddressBook
    book.add_record(record1)
    book.add_record(record2)
    book.add_record(record3)

    # Перевірка ітератора...виведення двох записів
    page_size = 2
    iterator = book.iterator(page_size)
    batch = next(iterator)
    print('Виведення більше одного запису(якщо є):')
    for record in batch:
        print(f"Name: {record.name.value}, "
              f"Phones: {', '.join((phone.value) for phone in record.phones)}, "
              f"Birthday: {record.birthday.value}")


    # Перевірка ітератора...виведення одного запису
    page_size = 1
    iterator = book.iterator(page_size)
    batch = next(iterator)
    for record in batch:
        print('___________\nВиведення одного запису: \n'
            f"Name: {record.name.value}, "
              f"Phones: {', '.join((phone.value) for phone in record.phones)}, "
              f"Birthday: {record.birthday.value}")

