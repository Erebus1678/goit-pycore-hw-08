from collections import UserDict
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value: str):
        value = value.strip()
        if not (value.isdigit() and len(value) == 10):
            raise ValueError("Invalid phone number. Phone must contain 10 digits.")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value: str):
        value = value.strip()
        try:
            dt = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(dt)

    def __str__(self) -> str:
        return self.value.strftime("%d.%m.%Y")


class Record:
    def __init__(self, name: str):
        self.name = Name(name.strip())
        self.phones: List[Phone] = []
        self.birthday: Optional[Birthday] = None

    def add_phone(self, phone: str) -> None:
        self.phones.append(Phone(phone))

    def remove_phone(self, phone: str) -> None:
        phone = phone.strip()
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return
        raise ValueError("Phone number not found.")

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        old_phone = old_phone.strip()
        for i, p in enumerate(self.phones):
            if p.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return
        raise ValueError("Old phone number not found.")

    def find_phone(self, phone: str) -> Optional[Phone]:
        phone = phone.strip()
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday: str) -> None:
        if self.birthday is not None:
            raise ValueError("Birthday is already set for this contact.")
        self.birthday = Birthday(birthday)

    def __str__(self) -> str:
        phones_str = ", ".join(str(p) for p in self.phones) if self.phones else "—"
        bday_str = str(self.birthday) if self.birthday else "—"
        return f"{self.name.value}: phones: {phones_str}; birthday: {bday_str}"


class AddressBook(UserDict):
    def add_record(self, record: Record) -> None:
        self.data[record.name.value] = record

    def find(self, name: str) -> Optional[Record]:
        return self.data.get(name.strip())

    def delete(self, name: str) -> None:
        name = name.strip()
        if name not in self.data:
            raise KeyError("Contact not found.")
        del self.data[name]

    def get_upcoming_birthdays(self, days: int = 7) -> List[Dict[str, str]]:

        today = date.today()
        end_date = today + timedelta(days=days)

        result: List[Dict[str, str]] = []

        for record in self.data.values():
            if not record.birthday:
                continue

            bday: date = record.birthday.value

            try:
                bday_this_year = bday.replace(year=today.year)
            except ValueError:
                bday_this_year = date(today.year, 2, 28)

            if bday_this_year < today:
                try:
                    bday_this_year = bday.replace(year=today.year + 1)
                except ValueError:
                    bday_this_year = date(today.year + 1, 2, 28)

            if today <= bday_this_year <= end_date:
                congrats_date = bday_this_year
                if congrats_date.weekday() == 5:
                    congrats_date += timedelta(days=2)
                elif congrats_date.weekday() == 6:
                    congrats_date += timedelta(days=1)

                result.append(
                    {
                        "name": record.name.value,
                        "congratulation_date": congrats_date.strftime("%d.%m.%Y"),
                    }
                )

        result.sort(key=lambda x: (datetime.strptime(x["congratulation_date"], "%d.%m.%Y").date(), x["name"]))
        return result
