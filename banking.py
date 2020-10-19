import random
import sqlite3
from string import digits


def sql_query(query, path='card.s3db'):
    connect = sqlite3.connect(path)
    cursor = connect.cursor()
    cursor.execute(query)
    connect.commit()
    connect.close()


def create_table(name, path='card.s3db'):
    query = f'''CREATE TABLE IF NOT EXISTS {name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number TEXT UNIQUE,
                pin TEXT,
                balance INTEGER DEFAULT 0
                );
                '''
    sql_query(query, path)


def delete_table(name, path='card.s3db'):
    query = f"DROP TABLE {name}"
    sql_query(query, path)


def loggin_user():
    print("Enter your card number:")
    number = input()
    print("Enter your pin:")
    pin = input()

    connect = sqlite3.connect('card.s3db')
    cursor = connect.cursor()
    query = '''SELECT number, pin FROM card'''
    cursor.execute(query)
    result = dict([n for n in cursor.fetchall()])
    connect.close()

    if number in result and pin == result[number]:
        user = Account()
        user.card_number = number
        print(f"\nYou have successfully logged in!\n")
        log_on_menu(user)
    else:
        print("\nWrong card number or pin\n")


def menu():
    while True:
        print("1. Create an account\n2. Log into account\n0. Exit")  # Main menu

        choice = int(input())
        print()

        if choice == 1:
            user = Account()
            user.create_account()
            del user
        elif choice == 2:
            loggin_user()
        elif choice == 0:
            print("Bye!")
            break


def log_on_menu(user):
    while True:
        print("1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit")

        choice = int(input())
        if choice == 1:
            print(f"\nYour balance is: {user.get_balance()}\n")
        elif choice == 2:
            user.income()
        elif choice == 3:
            print(user.transfer())
        elif choice == 4:
            print(user.delete_account())
            del user
            print()
            break
        elif choice == 5:
            del user
            print()
            break
        elif choice == 0:
            print(f"Bye!\n")
            exit()


class Account:
    def __init__(self):
        self.iin = self.can = self.checksum = None
        self.card_number = self.pin = self.balance = None

    def create_account(self):
        self.card_number = self.gen_number()
        self.pin = self.gen_pin()
        self.balance = 0
        self.add_account()
        print(f"Your card has been created\nYour card number:\n{self.card_number}\nYour card PIN:\n{self.pin}\n")

    def gen_number(self):
        self.iin = "400000"
        self.can = ''.join(random.choice(digits) for n in range(9))
        self.checksum = self.gen_checksum(self.iin + self.can)

        connect = sqlite3.connect('card.s3db')
        cursor = connect.cursor()
        query = '''SELECT number FROM card'''
        cursor.execute(query)
        result = [n[0] for n in cursor.fetchall()]
        connect.close()

        if self.iin + self.can + self.checksum in result:
            return self.gen_number()
        else:
            return self.iin + self.can + self.checksum

    @staticmethod
    def gen_checksum(digits15):
        if len(digits15) != 15:
            return None
        first = [int(value) * 2 if pos % 2 == 0 else int(value) for pos, value in enumerate(digits15)]
        second = [num - 9 if num >= 10 else num for num in first]
        number = 10 - sum(second) % 10
        return str(number)[-1]

    @staticmethod
    def gen_pin():
        return "{:04}".format(random.randint(0, 10000))

    def add_account(self):
        query = f'''INSERT INTO card (number, pin, balance)
                    VALUES ({self.card_number},{self.pin},{self.balance}
                    );'''
        sql_query(query)

    def get_balance(self):
        connect = sqlite3.connect('card.s3db')
        cursor = connect.cursor()
        query = f'''SELECT balance FROM card WHERE number = {self.card_number}'''
        cursor.execute(query)
        result = cursor.fetchone()[0]
        connect.close()
        return float(result)

    def income(self):
        print('\nEnter income:')
        money = float(input())
        query = f'UPDATE card SET balance = {self.get_balance() + money} WHERE number = {self.card_number}'
        sql_query(query)
        print('\nIncome was added!\n')

    def transfer(self):
        print('Enter card number:')
        receiver_number = input()

        if receiver_number == self.card_number:
            return "\nYou can't transfer money to the same account!\n"

        elif receiver_number[-1] != self.gen_checksum(receiver_number[:-1]):
            return '\nProbably you made a mistake in the card number. Please try again!\n'

        try:
            connect = sqlite3.connect('card.s3db')
            cursor = connect.cursor()
            query = f'''SELECT number FROM card WHERE number = {receiver_number}'''
            cursor.execute(query)
            result = cursor.fetchone()[0]
            connect.close()
        except TypeError:
            return '\nSuch a card does not exist.\n'

        if result != receiver_number:
            return '\nSuch a card does not exist.\n'

        print('Enter how much money you want to transfer:')
        money = int(input())

        if money > self.get_balance():
            return '\nNot enough money!\n'
        else:
            query = f'UPDATE card SET balance = balance - {money} WHERE number = {self.card_number}'
            sql_query(query)
            query = f'UPDATE card SET balance = balance + {money} WHERE number = {receiver_number}'
            sql_query(query)
            return '\nSuccess!\n'

    def delete_account(self):
        query = f'DELETE FROM card WHERE number = {self.card_number}'
        sql_query(query)
        return '\nThe account has been closed!\n'


# --------------------MAIN--------------------

try:
    delete_table('card', 'card.s3db')
except sqlite3.OperationalError:
    pass

create_table('card', 'card.s3db')

menu()
