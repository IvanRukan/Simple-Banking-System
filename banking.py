import random
from sqlalchemy import create_engine, String, Integer, Column, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
info = {}
id_table = random.randint(0, 9999)


class Card(Base):
    __tablename__ = 'card'

    id = Column(Integer, primary_key=True, default='')
    number = Column(Text)
    pin = Column(Text)
    balance = Column(Integer, default=0)


def luhn_generation():
    while True:
        number = '400000'
        for _ in range(10):
            number += str(random.randint(1, 9))
        result = number
        number = list(number)
        last_digit = int(number[-1])
        del number[-1]
        number = [int(each) for each in number]
        for index, each in enumerate(number):
            if index % 2 == 0:
                number[index] = each * 2
        for index, each in enumerate(number):
            if each > 9:
                number[index] = each - 9
        number.append(last_digit)
        if sum(number) % 10 == 0:
            return result


def luhn_validation(number):
    number = list(number)
    last_digit = int(number[-1])
    del number[-1]
    number = [int(each) for each in number]
    for index, each in enumerate(number):
        if index % 2 == 0:
            number[index] = each * 2
    for index, each in enumerate(number):
        if each > 9:
            number[index] = each - 9
    number.append(last_digit)
    if sum(number) % 10 == 0:
        return True


def card_generator():
    global id_table
    number = luhn_generation()
    pin = ''
    for _ in range(4):
        pin += str(random.randint(0, 9))
    info[number] = [pin, '0']
    print('Your card has been created')
    print('Your card number:')
    print(number)
    print('Your card PIN:')
    print(pin)
    session.add(Card(id=id_table, number=number, pin=pin))
    session.commit()
    id_table = random.randint(0, 9999)


def logging_in():
    print('Enter your card number:')
    number = input()
    print('Enter your PIN:')
    pin = input()
    for card, pin_balance in info.items():
        if number == card and pin == pin_balance[0]:
            print('You have successfully logged in!')
            card_interface(number, pin)
    print('Wrong card number or PIN!')
    return interface()


def interface():
    while True:
        print("""1. Create an account
2. Log into account
0. Exit
""")
        action = input()
        if action == '1':
            card_generator()
        elif action == '2':
            logging_in()
        elif action == '0':
            print('Bye!')
            exit()


def card_interface(number, pin):
    print("""1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit
""")
    action = input()
    if action == '1':
        return balance(number, pin)
    elif action == '2':
        return add_income(number, pin)
    elif action == '3':
        return transfer(number, pin)
    elif action == '4':
        delete(number, pin)
    elif action == '5':
        interface()
    elif action == '0':
        print('Bye!')
        exit()


def balance(number, pin):
    query = session.query(Card)
    bal = query.filter(Card.number == number and Card.pin == pin)
    for money in bal:
        print(f'Balance: {money.balance}')
    return card_interface(number, pin)


def add_income(number, pin):
    query = session.query(Card)
    card = query.filter(Card.number == number and Card.pin == pin)
    print('Enter income:')
    card.update({"balance": Card.balance + int(input())})
    session.commit()
    print('Income was added!')
    return card_interface(number, pin)


def transfer(number, pin):
    print('Transfer')
    print('Enter card number:')
    to_card = input()
    if not luhn_validation(list(to_card)):
        print('Probably you made a mistake in the card number. Please try again!')
        return card_interface(number, pin)
    query = session.query(Card)
    needed_card = query.filter(Card.number == to_card)
    search_result = False
    for card in needed_card:
        if card.number == to_card:
            search_result = True
            break
    if not search_result:
        print('Such a card does not exist.')
        return card_interface(number, pin)
    if number == to_card:
        print("You can't transfer money to the same account!")
        return card_interface(number, pin)
    print('How much do you want to transfer:')
    amount = int(input())
    from_bal = False
    needed_amount = query.filter(Card.number == number)
    for card in needed_amount:
        if card.balance >= amount:
            from_bal = True
            break
    if not from_bal:
        print('Not enough money!')
        return card_interface(number, pin)
    needed_amount.update({"balance": Card.balance - amount})
    needed_card.update({"balance": Card.balance + amount})
    session.commit()
    print('Success!')
    return card_interface(number, pin)


def delete(number, pin):
    query = session.query(Card)
    card = query.filter(Card.number == number and Card.pin == pin)
    card.delete()
    session.commit()
    print('The account has been closed!')
    return interface()


engine = create_engine('sqlite:///card.s3db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
interface()
