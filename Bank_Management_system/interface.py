import mysql.connector as mysql
from mysql.connector import Error
import random
from logo import logo



def db_connect(db_name):
    '''To establish connection with database and create table'''
    try:
        conn = mysql.connect(host = "localhost",
                             user = "root",
                             password = "root",
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
                          PRIMARY KEY (ACC_NUM))'''
            
            cursor.execute(create_query)
            cursor.execute(create_query_2)
        # print("Table created and accessible.\n")
        return conn
    except Error as e:
        print(e)



def add_new_cust(cursor):
    '''To add new customer data in the table'''
    total_amount = 0

    first_name = (input("Enter your First name: ")).title()
    last_name = (input("Enter your Last name: ")).title()
    phone = input("Enter your mobile num: ")
    initial_depo = int(input("Enter the amount which you want to deposit(min $1000): "))
    if initial_depo < 1000 or initial_depo <= 0:
        print("Invalid amount.")
        return
    total_amount = initial_depo + total_amount
    pin = int(input("Enter your 4 digit Pin: "))
    city = input("Enter your City name: ").title()
    state = input('Enter your State name: ').title()
    acc_num = random.randint(103938, 345325)
    new_cust = (acc_num, first_name, last_name, phone, pin, city, state, total_amount)

    query = ('''INSERT INTO bank_management.user_details(ACC_NUM, FIRST_NAME, LAST_NAME, PHONE, PIN, CITY, STATE, TOTAL_AMOUNT)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''')
    cursor.execute(query, (new_cust))
    print("New User created!")
    print(f"Welcome {first_name} to Corporate Bank. {acc_num} is your account number.\n")
    login_menu()



def login_cust(cursor):
    '''To Login users using Acc num and Pin'''
    acc_num = int(input("Enter your Account number to login: "))
    pin = int(input("Enter your Pin to login: "))
    cursor.execute('SELECT * FROM bank_management.user_details WHERE ACC_NUM = %s AND PIN = %s', (acc_num, pin))
    checkAccNum = cursor.fetchone()
    if checkAccNum == 0:
        print("User does not exist.")
    else:
        print("User exist.")
    
    while True:
        user_input = input('''Select any "one" from below menu:
--> Press 1 for money deposit
--> Press 2 for money withdraw
--> Press 3 to check Available balance
--> Press 4 to check account info
--> Press 5 to Exit the menu                           
''')
        if user_input == '1':
            total_balance = 0
            current_balance = 0
            amount = int(input("Enter the amount you want to deposit: $"))
            if amount > 0:
                print('Depositing Money...')
                cursor.execute('SELECT total_amount FROM bank_management.user_details WHERE ACC_NUM = %s and PIN = %s', (acc_num, pin))
                result = cursor.fetchone()
                for i in result:
                    current_balance = i
                total_balance = current_balance + amount
                query = ('UPDATE bank_management.user_details SET total_amount = %s WHERE acc_num = %s')
                val = (total_balance, acc_num)
                cursor.execute(query, val)
                print('Done')
                cursor.execute('SELECT * FROM bank_management.user_details WHERE ACC_NUM = %s AND PIN = %s', (acc_num, pin))
                result_2 = cursor.fetchone()
                print(f'Your current balance is ${total_balance}')
            else:
                print('Invalid amount transaction aborted!')
        elif user_input == '2':
            left_balance = 0
            current_balance = 0
            amount = int(input("Enter the amount you want to withdraw: "))
            cursor.execute('SELECT total_amount FROM bank_management.user_details WHERE ACC_NUM = %s and PIN = %s', (acc_num, pin))
            result = cursor.fetchone()
            for i in result:
                current_balance = i
            if amount > 0 and amount <= current_balance:
                left_balance = current_balance - amount
                print(f'Your total balance is ${left_balance}. Your have withdrawn total amount of ${amount}.')
                query = ('UPDATE bank_management.user_details SET total_amount = %s WHERE acc_num = %s AND pin = %s')
                val = (left_balance, acc_num, pin)
                cursor.execute(query, val)
                print('Done')
            else:
                print('Invalid amount transaction aborted!')
        elif user_input == '3':
            current_balance = 0
            cursor.execute('SELECT total_amount FROM bank_management.user_details WHERE ACC_NUM = %s and PIN = %s', (acc_num, pin))
            result = cursor.fetchone()
            for i in result:
                current_balance = i
            print(f'Your available balance is ${current_balance}.')
        elif user_input == '4':
            cursor.execute('SELECT * FROM bank_management.user_details WHERE ACC_NUM = %s AND PIN = %s', (acc_num, pin))
            result = cursor.fetchall()
            for row in result:
                print("Account Num: ", row[0])
                print("First Name: ", row[1])
                print("Last Name: ", row[2])
                print("Phone Num: ", row[3])
                print("City: ", row[5])
                print("State: ", row[6])
                print("Total Amount: ", row[7])
                print("\n")
        elif user_input == '5':
            print('Exiting...')
            break
        else:
            print('Invalid input. Please check again.')
    login_menu()


def acc_hold(cursor):
    '''To check the count of available account holders'''
    current_count = 0
    cursor.execute('''select count(ACC_NUM) from bank_management.user_details''')
    output = cursor.fetchone()
    for i in output:
        current_count = i
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

    # if checkAccNum == 0:
    #     print('Invalid input. Please check again.')
    # else:
    #     print('User exist.')

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
            print('Creating a new customer...')
            return add_new_cust(cursor)
        elif user_input1 == '2':
            print('Logging in as existing customer...')
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
    print(logo)
    login_menu()


db = db_connect("bank_management")
cursor = db.cursor()
interface()
db.commit()
db.close()
