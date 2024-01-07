import mysql.connector as mysql
from mysql.connector import Error
from sqlalchemy import create_engine
import pandas as pd
import random, re
from logo import logo

def db_connect(db_name):
    '''To establish connection with database and create table'''
    try:
        conn = mysql.connect(host = "localhost",
                             user = "root",
                             password = "Tarangkr",
                             database = db_name)
        if conn.is_connected():
            # print('Database is connected!')
            cursor = conn.cursor()
            create_query = '''CREATE TABLE IF NOT EXISTS user_details (
                          ACC_NUM INT NOT NULL,
                          FIRST_NAME VARCHAR(30) NOT NULL,
                          LAST_NAME VARCHAR(30) NOT NULL,
                          PHONE CHAR(255) NOT NULL,
                          PIN INT NOT NULL,
                          CITY VARCHAR(30),
                          STATE VARCHAR(30),
                          TOTAL_AMOUNT INT,
                          ACC_CREATION DATETIME,
                          PRIMARY KEY (ACC_NUM))'''
            
            create_query_2 = '''CREATE TABLE IF NOT EXISTS deleted_user_details (
                          ACC_NUM INT NOT NULL,
                          FIRST_NAME VARCHAR(30) NOT NULL,
                          LAST_NAME VARCHAR(30) NOT NULL,
                          PHONE CHAR(255) NOT NULL,
                          PIN INT NOT NULL,
                          CITY VARCHAR(30),
                          STATE VARCHAR(30),
                          TOTAL_AMOUNT INT,
                          ACC_CREATION DATETIME,
                          PRIMARY KEY (ACC_NUM))'''
            
            cursor.execute(create_query)
            cursor.execute(create_query_2)
        # print("Table created and accessible.\n")
        return conn
    except Error as e:
        print(e)


def validate_mobile_number(phone):
        '''To validate mobile number length'''
        pattern = re.compile(r'^\d{10}$')
        return bool(pattern.match(phone))


def add_new_cust(cursor):
    '''To add new customer data in the table'''
    total_amount = 0

    first_name = (input("Enter your First name: ")).title()
    last_name = (input("Enter your Last name: ")).title()
    phone = input("Enter your mobile num: ")
    # validating phone_number length
    if validate_mobile_number(phone):
        pass
    else:
        print(f"{phone} is an invalid mobile number")
    initial_depo = int(input("Enter the amount which you want to deposit(min $1000): "))
    # validating amount for deposit
    if initial_depo < 1000 or initial_depo <= 0:
        print("Invalid amount.")
        return
    total_amount = initial_depo + total_amount
    pin = int(input("Enter your 4 digit Pin: "))
    # validating pin length
    mystr = str(pin)
    if len(mystr) == 4:
        pass
    else:
        print('Please enter only 4 digit pin.1')
    city = input("Enter your City name: ").title()
    state = input('Enter your State name: ').title()
    acc_num = random.randint(100001, 345325)

    # establishing connection with mySQL database
    engine = create_engine("mysql+pymysql://root:Tarangkr@127.0.0.1:3306/bank_management")
    # using pandas to add column and insert data in database for new user
    data = {'ACC_NUM': [acc_num],
            'FIRST_NAME': [first_name],
            'LAST_NAME': [last_name],
            'PHONE': [phone],
            'PIN': [pin],
            'CITY': [city],
            'STATE': [state],
            'TOTAL_AMOUNT': [total_amount]}
    df = pd.DataFrame(data, columns= ['ACC_NUM', 'FIRST_NAME', 'LAST_NAME', 'PHONE', 'PIN', 'CITY', 'STATE', 'TOTAL_AMOUNT'])
    df['ACC_CREATION'] = pd.Timestamp('now').today()
    df.to_sql(name='user_details', con = engine, if_exists = 'append', chunksize = 1000, index=False)
    print("New User created!\n")
    print(f"Welcome {first_name} to Corporate Bank. '{acc_num}' is your account number with ${total_amount} as total balance.\n")
    # df = pd.read_sql("SELECT * FROM bank_management.user_details", con=engine)
    # print(df.head())
    login_menu()



def login_cust(cursor):
    '''To Login users using Acc num and Pin'''
    acc_num = int(input("Enter your Account number to login: "))
    pin = int(input("Enter your Pin to login: "))
    engine = create_engine("mysql+pymysql://root:Tarangkr@127.0.0.1:3306/bank_management")
    # establishing connection with mySQL database
    query = "SELECT * FROM bank_management.user_details WHERE ACC_NUM = '%s' AND PIN = '%s'" % (acc_num, pin)
    df = pd.read_sql(query, con=engine)
    # validating user exist in db
    if df.empty:
        print('User does not exist.\n')
        return bool
    else:
        print('User exist.\n')
    
    # printing user menu after logging in
    while True:
        user_input = input('''Select any "one" from below menu:
--> Press 1 for money deposit
--> Press 2 for money withdraw
--> Press 3 to check Available balance
--> Press 4 to check account info
--> Press 5 to Exit the menu                           
\n''')
        if user_input == '1':
            total_balance = 0
            current_balance = 0
            amount = int(input("Enter the amount you want to deposit: $"))
            if amount > 0:
                print('Depositing Money...\n')
                # checking for total amount of existing user
                amount_query = "SELECT total_amount FROM bank_management.user_details WHERE ACC_NUM = '%s' and PIN = '%s'" % (acc_num, pin)
                current_balance = pd.read_sql(amount_query, con=engine).values[0][0]
                total_balance = current_balance + amount
                change_balance = int(total_balance)
                # updating database with deposited amount
                update_query = ('UPDATE bank_management.user_details SET total_amount = %s WHERE acc_num = %s')
                val = (change_balance, acc_num)
                cursor.execute(update_query, val)
                print('Amount Deposited!\n')
                # returning updated amount to user
                check_query = "SELECT * FROM bank_management.user_details WHERE ACC_NUM = '%s' and PIN = '%s'" % (acc_num, pin)
                df = pd.read_sql(check_query, con=engine)
                print(f'Your current balance is ${change_balance} for Acc. num: {acc_num}.')
            else:
                print('Invalid amount transaction aborted!')
        elif user_input == '2':
            left_balance = 0
            current_balance = 0
            # checking for total amount of existing user
            amount = int(input("Enter the amount you want to withdraw: "))
            amount_query2 = "SELECT total_amount FROM bank_management.user_details WHERE ACC_NUM = '%s' and PIN = '%s'" % (acc_num, pin)
            current_balance2 = pd.read_sql(amount_query2, con=engine).values[0][0]
            change_balance2 = int(current_balance2)
            # checking if entered amount is valid or not
            if amount > 0 and amount <= change_balance2:
                left_balance = change_balance2 - amount
                print(f'\nYour total balance is ${left_balance} for Acc. num: {acc_num}. Your have withdrawn total amount of ${amount}.\n')
                # updating database after withdrawl amount
                query = ('UPDATE bank_management.user_details SET total_amount = %s WHERE acc_num = %s AND pin = %s')
                val = (left_balance, acc_num, pin)
                cursor.execute(query, val)
                print('Transaction Completed!\n')
            else:
                print('Invalid amount transaction aborted!')
        elif user_input == '3':
            current_balance3 = 0
            # to check current balance of user
            amount_query3 = "SELECT total_amount FROM bank_management.user_details WHERE ACC_NUM = '%s' and PIN = '%s'" % (acc_num, pin)
            current_balance3 = pd.read_sql(amount_query3, con=engine).values[0][0]
            change_balance = int(current_balance3)
            print(f'Your available balance is ${current_balance3}.')
        elif user_input == '4':
            # to display user account info
            query = "SELECT * FROM bank_management.user_details WHERE ACC_NUM = '%s' AND PIN = '%s'" % (acc_num, pin)
            df = pd.read_sql(query, con=engine)
            for i in range(len(df)):
                print("Account number: ", df.loc[i, "ACC_NUM"])
                print("First name: ", df.loc[i, "FIRST_NAME"])
                print("Last name: ", df.loc[i, "LAST_NAME"])
                print("Phone: ", df.loc[i, "PHONE"])
                print("City: ", df.loc[i, "CITY"])
                print("State: ", df.loc[i, "STATE"])
                print("Total Amount: $",df.loc[i, "TOTAL_AMOUNT"])
            print("\n")
        elif user_input == '5':
            # to exit the current menu
            print('Exiting...')
            break
        else:
            print('Invalid input. Please check again.')
    login_menu()



def acc_hold(cursor):
    '''To check the count of available account holders'''
    current_count = 0
    engine = create_engine("mysql+pymysql://root:Tarangkr@127.0.0.1:3306/bank_management")
    query = "select count(ACC_NUM) from bank_management.user_details"
    total_users = pd.read_sql(query, con=engine).values[0][0]
    current_count = int(total_users)
    print(f"There are currently '{current_count}' active account holders in the bank.")
    login_menu()



def acc_close(cursor):
    '''To close the account from the Bank'''
    acc_num = int(input("Enter your Account number to Close the Account: "))
    pin = int(input("Enter your Pin: "))
    cursor.execute('SELECT * FROM bank_management.user_details WHERE ACC_NUM = %s AND PIN = %s', (acc_num, pin))
    checkAccNum = cursor.fetchone()
    if checkAccNum == 0:
        print('Invalid input. Please check again.')
    else:
        cursor.execute('INSERT INTO bank_management.deleted_user_details SELECT * FROM bank_management.user_details WHERE acc_num = %s AND pin = %s', (acc_num, pin))
        cursor.execute('DELETE FROM bank_management.user_details WHERE acc_num = %s AND pin = %s', (acc_num, pin))
        print(f'Account has been closed for {acc_num}. Happy to help!')
    login_menu()



def money_transfer(cursor):
    '''To transfer money within existing users'''
    payee_left_balance = 0
    payee_current_balance = 0

    acc_num = int(input("Enter your Account number for Money Transfer: "))
    pin = int(input("Enter your Pin: "))
    amount_to_transfer = int(input('Enter the amount you want to transfer: $'))
    cursor.execute('SELECT * FROM bank_management.user_details WHERE ACC_NUM = %s AND PIN = %s', (acc_num, pin))
    checkAccNum = cursor.fetchone()
    if amount_to_transfer > 0 and checkAccNum != 0:
        print('Checking available balance for transfer...')
        cursor.execute('SELECT total_amount FROM bank_management.user_details WHERE ACC_NUM = %s and PIN = %s', (acc_num, pin))
        result = cursor.fetchone()
        for i in result:
            payee_current_balance = i
        print('Done')
    else:
        print('User does not exist or entered amount exceeds available amount.')

    while True:
        receiver_left_balance = 0
        receiver_current_balance = 0
        user2_acc_num = int(input("Enter Receiver's Account number: "))
        user2_first_name = input("Enter Receiver's First name: ").title()
        user2_last_name = input("Enter Receiver's Last name: ").title()
        cursor.execute('SELECT * FROM bank_management.user_details WHERE ACC_NUM = %s AND FIRST_NAME = %s AND LAST_NAME = %s', (user2_acc_num, user2_first_name, user2_last_name))
        check = cursor.fetchone()
        if check == 0 and amount_to_transfer > 0:
            print('Receiver account does not exist. Please try again!')
        elif check != 0 and amount_to_transfer < 0:
            print('Invalid amount entered. Please enter valid amount.')
        else:
            if amount_to_transfer > 0 and amount_to_transfer <= payee_current_balance:
                payee_left_balance = payee_current_balance - amount_to_transfer
                print(f'Your total balance is ${payee_left_balance}. Your have transfer total amount of ${amount_to_transfer}.')
                payee_query = ('UPDATE bank_management.user_details SET total_amount = %s WHERE acc_num = %s')
                val = (payee_left_balance, acc_num)
                cursor.execute(payee_query, val)
                print('Done')
                cursor.execute('SELECT total_amount FROM bank_management.user_details WHERE ACC_NUM = %s and FIRST_NAME = %s', (user2_acc_num, user2_first_name))
                result2 = cursor.fetchone()
                for i in result2:
                    receiver_left_balance = i
                receiver_current_balance = receiver_left_balance + amount_to_transfer
                receiver_query = ('UPDATE bank_management.user_details SET total_amount = %s WHERE ACC_NUM = %s AND FIRST_NAME = %s AND LAST_NAME = %s')
                val2 = (receiver_current_balance, user2_acc_num, user2_first_name, user2_last_name)
                cursor.execute(receiver_query, val2)
                print(f'Money transfer is successful. {acc_num} has successfully transferred ${amount_to_transfer} to {user2_acc_num}.')
                break
    login_menu()



def login_menu():
    '''To display login menu for Customers'''
    while True:
        user_input1 = input('''
<<<<<<<<<<<<<<<<< Welcome To Corporate Bank >>>>>>>>>>>>>>>>>>>>\n
Select any "one" from below menu:
--> Press 1 for Creating a new account
--> Press 2 for logging in as existing customer
--> Press 3 for displaying total number of customers
--> Press 4 for Money Transfer 
--> Press 5 to Close your account from the bank
--> Press 6 to "Exit" Menu\n\n''')
        
        if user_input1 == '1':
            print('Creating a new account...')
            return add_new_cust(cursor)
        elif user_input1 == '2':
            print('Logging in as existing customer...\n')
            return login_cust(cursor)
        elif user_input1 == '3':
            return acc_hold(cursor)
        elif user_input1 == '4':
            return money_transfer(cursor)
        elif user_input1 == '5':
            return acc_close(cursor)
        elif user_input1 == '6':
            print('Exiting...')
            break
        else:
            print('Invalid input. Please check again.')
        print('\n**********************************************************************\n')

def interface():
    '''To Print logo at start of the application'''
    print(logo)
    login_menu()

db = db_connect("bank_management")
cursor = db.cursor()
interface()
db.commit()
db.close()

