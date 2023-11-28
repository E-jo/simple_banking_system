import random
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Text
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

Base = declarative_base()


class Card(Base):
    __tablename__ = 'card'

    id = Column(Integer, primary_key=True)
    number = Column(Text)
    pin = Column(Text)
    balance = Column(Integer)


engine = create_engine('sqlite:///card.s3db')
if not database_exists(engine.url):
    create_database(engine.url)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


def main_menu():
    print("1. Create an account")
    print("2. Log into account")
    print("0. Exit")
    choice = input()
    if choice == "1":
        create_account()
    elif choice == "2":
        log_in()
    elif choice == "0":
        print("Bye!")
        session.close()
        exit(0)


def customer_menu(card_number):
    print("1. Balance")
    print("2. Add income")
    print("3. Do transfer")
    print("4. Close account")
    print("5. Log out")
    print("0. Exit")
    choice = input()
    if choice == "1":
        balance = get_balance(card_number)
        print("Balance: " + str(balance))
        customer_menu(card_number)
    elif choice == "2":
        add_income(card_number)
        customer_menu(card_number)
    elif choice == "3":
        do_transfer(card_number)
    elif choice == "4":
        close_account(card_number)
        main_menu()
    elif choice == "5":
        print("You have successfully logged out!")
        main_menu()
    elif choice == "0":
        print("Bye")
        session.close()
        exit(0)


def check_luhn(card_number):
    card_number_list = list(card_number)

    for i in range(len(card_number_list)):
        if (i + 1) % 2 != 0:
            card_number_list[i] = str(int(card_number_list[i]) * 2)

    for i in range(len(card_number_list)):
        if int(card_number_list[i]) > 9:
            card_number_list[i] = str(int(card_number_list[i]) - 9)

    list_sum = 0
    for i in range(len(card_number_list)):
        list_sum += int(card_number_list[i])
    return list_sum % 10 == 0


def do_transfer(card_number):
    print("Transfer")
    print("Enter card number")
    destination_num = input()

    if not check_luhn(destination_num):
        print("Probably you made a mistake in the card number. Please try again!")
        customer_menu(card_number)

    query = session.query(Card)
    destination = query.filter(Card.number == destination_num)

    if destination.first() is None:
        print("Such a card does not exist.")
        customer_menu(card_number)

    if destination_num == card_number:
        print("You can't transfer money to the same account!")
        customer_menu(card_number)

    print("Enter how much money you want to transfer:")
    amt = int(input())

    customer = query.filter(Card.number == card_number)
    if customer.first().balance < amt:
        print("Not enough money!")
        customer_menu(card_number)

    customer.update({"balance": Card.balance - amt})
    session.commit()

    destination.update({"balance": Card.balance + amt})
    session.commit()

    print("Success!")
    customer_menu(card_number)


def add_income(card_number):
    print("Enter income:")
    income = int(input())
    query = session.query(Card)
    customer = query.filter(Card.number == card_number)
    customer.update({"balance": Card.balance + income})
    session.commit()
    print("Income was added!")


def close_account(card_number):
    query = session.query(Card)
    customer = query.filter(Card.number == card_number)
    customer.delete()
    session.commit()
    print("The account has been closed!")


def get_balance(card_number):
    query = session.query(Card)
    for row in query.filter(Card.number == card_number):
        return row.balance


def create_account():
    global c_a_n
    card_number = "400000"

    unique = False
    customer_account_nums = []

    query = session.query(Card)
    for row in query:
        customer_account_nums.append(row.number)

    while not unique:
        c_a_n = ""
        for i in range(9):
            c_a_n += str(random.randint(0, 9))
        if c_a_n not in customer_account_nums:
            customer_account_nums.append(c_a_n)
            unique = True
    card_number += c_a_n
    check_sum = generate_checksum(card_number)
    card_number += str(check_sum)

    pin = ""
    for i in range(4):
        pin += str(random.randint(0, 9))

    print("Your card has been created")
    print("Your card number:")
    print(card_number)
    print("Your card pin:")
    print(pin)

    new_card = Card(number=card_number, pin=pin, balance=0)
    session.add(new_card)
    session.commit()

    main_menu()


def generate_checksum(card_number):
    # generate checksum digit for Luhn algorithm
    card_number_list = list(card_number)

    for i in range(len(card_number_list)):
        if (i + 1) % 2 != 0:
            card_number_list[i] = str(int(card_number_list[i]) * 2)

    for i in range(len(card_number_list)):
        if int(card_number_list[i]) > 9:
            card_number_list[i] = str(int(card_number_list[i]) - 9)

    list_sum = 0
    for i in range(len(card_number_list)):
        list_sum += int(card_number_list[i])

    check_sum = 0
    while (list_sum + check_sum) % 10 != 0:
        check_sum += 1

    return check_sum


def log_in():
    print("Enter your card number:")
    card_num = input()
    print("Enter your PIN:")
    pin = input()

    query = session.query(Card)
    query = query.filter(Card.number == card_num)

    for row in query:
        if row.pin == pin:
            print("You have successfully logged in!")
            customer_menu(card_num)

    print("Wrong card number or PIN!")
    main_menu()


main_menu()

