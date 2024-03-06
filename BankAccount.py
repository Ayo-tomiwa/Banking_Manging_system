import csv
import getpass
import random
from typing import Dict
import hashlib

class BankAccount:
    def __init__(self, account_name, account_number, account_type, initial_balance, personal_info, pin):
        self.account_name = account_name
        self.account_number = account_number
        self.account_type = account_type
        self.balance = initial_balance
        self.personal_info = personal_info
        self.transaction_history = []
        self.pin_hash = self._hash_pin(pin) # Hash the PIN for storage
        
    def _hash_pin(self, pin):
        """Hash the PIN using SHA-256 for storage."""
        return hashlib.sha256(pin.encode()).hexdigest()

    def authenticate(self, pin_attempt):
        """Authenticate the user by comparing the hash of the provided PIN with the stored hash."""
        pin_hash_attempt = self._hash_pin(pin_attempt)
        return self.pin_hash == pin_hash_attempt

    def deposit(self, amount):
        self.balance += amount
        self.transaction_history.append(f"Deposit: +{amount}")

    def withdraw(self, amount): 
        if self.balance >= amount:
            self.balance -= amount
            self.transaction_history.append(f"Withdrawal: -{amount}")
        else:
            print("Insufficient balance!")


    def get_account_info(self):
        return f"Account Name: {self.account_name}\nAccount Number: {self.account_number}\nAccount Type: {self.account_type}\nBalance: {self.balance}"
    
    def get_transaction_history(self): 
        return self.transaction_history

    def _record_transaction(self, transaction):
        with open(f"{self.account_number}transactions.csv", mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([transaction])
            
    def _get_valid_pin(self):
        while True:
            pin = getpass.getpass("Choose a 4-digit PIN: ")
            pin_hash = self._hash_pin(pin)  # Hash the PIN for storage
            if pin.isdigit() and len(pin) == 4:
                return pin
            print("Invalid PIN! Please enter a 4-digit number.")


class BankManagementSystem:
    def __init__(self):
        main_menu(self)
        self.accounts: Dict[str, BankAccount] = {}
        self.employees: Dict[str, dict] = {}
        self.load_accounts_from_csv()  # Load accounts from CSV file when initialized
        self.load_employees_from_csv()  # Load employees from CSV file when initialized


    def create_account(self):
        bank_account = BankAccount('', '', '', 0, '', '')  # Create a BankAccount instance

        account_name = input("Enter your full name: ")
        account_type = input("Enter account type (e.g., savings or current): ")
        initial_balance = float(input("Enter initial balance: "))
        personal_info = input("Enter personal info (e.g., married or single): ")
        pin = bank_account._get_valid_pin() # Call _get_valid_pin() from the BankAccount instance
        account_number = self._generate_account_number()
        
        account = BankAccount(account_name, account_number, account_type, initial_balance, personal_info, pin)
        self.accounts[account_number] = account
        
        print("Account created successfully!")
        print("Your account number is:", account_number)
        print("Remember to keep your PIN safe.")
        
        # Write account information to CSV file
        self._save_account_info(account_name, account_number, account_type, initial_balance, personal_info, pin)
        

    def _generate_account_number(self):
        while True:
            account_number = f'2000{random.randint(100000, 999999)}'
            if account_number not in self.accounts:
                return account_number

    def load_accounts_from_csv(self):
            with open('account_info.csv', mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    account_name = row['account_name']
                    account_number = row['account_number']
                    account_type = row['account_type']
                    initial_balance = float(row['initial_balance'])
                    personal_info = row['personal_info']
                    pin = row['pin']
                    account = BankAccount(account_name, account_number, account_type, initial_balance, personal_info, pin)
                    self.accounts[account_number] = account
            
    def save_account_to_csv(self, account):
        with open('account_info.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([account.account_name, account.account_number, account.account_type, account.balance, account.personal_info, account.pin])

   
    def _save_account_info(self, account_name, account_number, account_type, initial_balance, personal_info, pin):
        with open('account_info.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([account_name, account_number, account_type, initial_balance, personal_info, pin])

    def view_all_accounts(self):
        for self.account_number, account in self.accounts.items():
            print(account.get_account_info())
            print()
            
                 
    def deposit(self, account_number, amount): 
        account = self.accounts.get(account_number)
        if account:
            account.deposit(amount)
            return True
        return False
    
    def withdraw(self, account_number, amount):
        account = self.accounts.get(account_number)
        if account:
            account.withdraw(amount)
            return True
        return False

    def transfer(self, sender_account_number, recipient_account_number, amount, sender_pin):
        sender_account = self.accounts.get(sender_account_number)
        recipient_account = self.accounts.get(recipient_account_number)
        
        if sender_account and recipient_account and sender_account.authenticate(sender_pin):
            sender_account.withdraw(amount)
            recipient_account.deposit(amount)
            self._record_transaction(sender_account_number, f"Transfer: -{amount} to {recipient_account_number}")
            self._record_transaction(recipient_account_number, f"Transfer: +{amount} from {sender_account_number}")
            print("Transfer successful!")
            return True
        else:
            print("Transfer failed! Check account numbers or balances.")
            return False 

    def close_account(self, account_number): 
        if account_number in self.accounts:
            del self.accounts[account_number]
            print("Account closed successfully.")
        else:
            print("Account not found.")
         
    def get_account_info(self, account_number):
        account = self.accounts.get(account_number)
        if account:
            return account.get_account_info()
        return "Account not found!"
   
    
    def _record_transaction(self, account_number, transaction):
        with open(f"{account_number}transactions.csv", mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([transaction])
    
    
    def update_account_info(self, account_number):
        account = self.accounts.get(account_number)
        if account:
            print("Current Account Info:")
            print(account.get_account_info())
            print()
            choice = input("What information would you like to update? (balance, status, or transaction history): ").lower()
            if choice == "balance":
                new_balance = float(input("Enter the new balance: "))
                account.balance = new_balance
                print("Balance updated successfully!")
            elif choice == "status":
                new_status = input("Enter the new status: ")
                account.account_type = new_status
                print("Account status updated successfully!")
            elif choice == "transaction history":
                print("Transaction history cannot be manually updated.")
            else:
                print("Invalid choice!")
        else:
            print("Account not found!")
            
            
    def log_in(self, account_number, pin):
        account = self.accounts.get(account_number)
        if account and account.authenticate(pin):
            return True
        return False

    
    def customer_service(self):
        print("Welcome to Customer Service!")
        print("How can we assist you today?\n ")
        
        while True:
            print("1. Account inquiries")
            print("2. Transaction issues")
            print("3. General assistance")
            print("4. Go back to main menu\n ")
            
            choice = input("Enter your choice: ")
            
            if choice == "1":
                account_number = input("Enter your account number: ")
                account = self.accounts.get(account_number)
                if account:
                    print(account.get_account_info())
                else:
                    print("Account not found!")
            elif choice == "2":
                print("Please type your transaction issue.")
                transaction_issue = input("Type your transaction issue: ")
                print("Transaction issue recorded successfully!\n")
                # Placeholder code to handle transaction issues
                print(f"Transaction issue: {transaction_issue}. Our support team will contact you shortly.\n")
            elif choice == "3":
                print("Type your assistance request.")
                assistance_request = input("Type your assistance request: ")
                print("Assistance request recorded successfully!\n")
                # Placeholder code to provide general assistance
                print(f"Assistance request: {assistance_request}. We'll do our best to help you.\n")
            elif choice == "4":
                print("Returning to the main menu...\n ")
                break
            else:
                print("Invalid choice. Please enter a valid option.\n ")
                
    def create_employee_account(self):
        bank_account = BankAccount('', '', '', 0, '', '')  # create a BankAccount instance
        pin = bank_account._get_valid_pin()  # call _get_valid_pin() from the BankAccount instance

        employee_id = input("Enter employee ID: ")
        name = input("Enter employee name: ")
        position = input("Enter employee position:\n 1.Loan officers\n 2.Credit analyst\n 3.Bank teller\n 4.Accountant\n 5.bank manager\n 6.If not found in the option, add your position.\n")
        contact_info = input("Enter employee contact information: ")
        email = input("Enter employee email address: ")
        location = input("Enter employee location: ")
        password = getpass.getpass("Enter password: ")

    # Save employee information to CSV
        with open('employee_info.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([employee_id, name, position, contact_info, email, location, hashlib.sha256(password.encode()).hexdigest()])

        print("Employee account created successfully!\n")


        self.employees[employee_id] = {
            "name": name,
            "position": position,
            "contact_info": contact_info,
            "pin": pin
        }
        print("Employee account created successfully!\n ")
        # Write employee information to CSV file
        self._save_employee_info(employee_id, name, position, contact_info, pin)

        # After creating an employee account, allow the branch manager to perform administrative tasks
        if position.lower() == "bank manager":
            self.admin_tasks()
            
    def employee_login(self):
        employee_id = input("Enter your employee ID: ")
        password = getpass.getpass("Enter your password: ")
        employee = self.employees.get(employee_id)

        if employee and employee['password'] == hashlib.sha256(password.encode()).hexdigest():
            print("You have successfully logged in!\n ")

            # Based on the employee's role, provide access to specific functionalities
            if employee['position'].lower() == 'loan manager':
                self.loan_manager_menu()
            elif employee['position'].lower() == 'credit analyst':
                self.credit_analyst_menu()
            elif employee['position'].lower() == 'bank teller':
                self.bank_teller_menu()
            elif employee['position'].lower() == 'accountant':
                self.accountant_menu()
            elif employee['position'].lower() == 'bank manager':
                self.admin_tasks() 
                self.ban() # Assuming bank managers have administrative tasks access
            else:
               print("You don't have any functionality task yet")# Call custom position tasks for unknown positions
        else:
            print("Login failed. Please check your employee ID and PIN.\n ")
            

    def view_all_employees(self):
        print("All Employees:")
        for employee_id, employee in self.employees.items():
            print(f"Employee ID: {employee_id}")
            print(f"Name: {employee['name']}")
            print(f"Position: {employee['position']}")
            print(f"Contact Info: {employee['contact_info']}")
            print()

    def update_employee_info(self, employee_id):
        employee = self.employees.get(employee_id)
        if employee:
            print("Current Employee Info:")
            print(f"Employee ID: {employee_id}")
            print(f"Name: {employee['name']}")
            print(f"Position: {employee['position']}")
            print(f"Contact Info: {employee['contact_info']}")
            print()
            choice = input("What information would you like to update? (name, position, or contact info): ").lower()
            if choice == "name":
                new_name = input("Enter the new name: ")
                employee['name'] = new_name
                print("Name updated successfully!")
            elif choice == "position":
                new_position = input("Enter the new position: ")
                employee['position'] = new_position
                print("Position updated successfully!")
            elif choice == "contact info":
                new_contact_info = input("Enter the new contact info: ")
                employee['contact_info'] = new_contact_info
                print("Contact info updated successfully!")
            else:
                print("Invalid choice!")
        else:
            print("Employee not found!")

    def delete_employee_account(self, employee_id):
        if employee_id in self.employees:
            del self.employees[employee_id]
            print("Employee account deleted successfully.")
        else:
            print("Employee account not found.")

    def load_employees_from_csv(self):
        with open('employee_info.csv', mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                employee_id, name, position, contact_info, pin = row
                self.employees[employee_id] = {
                    "name": name,
                    "position": position,
                    "contact_info": contact_info,
                    "pin": pin
                }
                
                
    def load_accounts_from_csv(self):
        with open('employee_info.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if 'employee_id' in row:  # Check if 'employee_id' exists in the row
                    self.employees[row['employee_id']] = row
                else:
                    print("Error: 'employee_id' column not found in CSV file.")


    def save_employee_to_csv(self, employee):
        with open('employee_info.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([employee['employee_id'], employee['name'], employee['position'], employee['contact_info'], employee['pin']])

    def _save_employee_info(self, employee_id, name, position, contact_info, pin):
        with open('employee_info.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([employee_id, name, position, contact_info, pin])
            

    # Implement access control for managing employee accounts
    def manage_employee_accounts(self, current_user_position):
        # Check if the current user is the branch manager
        # Assuming the current user is authenticated and their position is known
        if current_user_position.lower() != "branch manager":
            print("Access denied! Only the branch manager can manage employee accounts.")
            return

        print("\nManaging Employee Accounts:")
        print("1. Create a new employee account")
        print("2. View all employee accounts")
        print("3. Update employee account information")
        print("4. Delete an employee account")
        print("5. Back to administrative tasks\n ")

        choice = input("Enter your choice: ")
        if choice == "1":
            self.create_employee_account()
        elif choice == "2":
            self.view_all_employees()
        elif choice == "3":
            employee_id = input("Enter employee ID: ")
            self.update_employee_info(employee_id)
        elif choice == "4":
            employee_id = input("Enter employee ID: ")
            self.delete_employee_account(employee_id)
        elif choice == "5":
            print("Returning to administrative tasks...\n ")
        else:
            print("Invalid choice. Please enter a valid option.\n ")

    # Modify the admin_tasks method to include the management of employee accounts
    def admin_tasks(self):
        print("\nAdministrative Tasks:")
        print("1. Managing employee accounts")
        print("2. Monitoring and auditing transactions")
        print("3. Generating reports")
        print("4. Configuring system parameters")
        print("5. View all employees")
        print("6. Back to main menu\n ")

        admin_choice = input("Enter your choice: ")
        if admin_choice == "1":
            # Access to managing employee accounts restricted to the branch manager
            self.manage_employee_accounts()
        elif admin_choice == "2":
            self.monitor_transactions()
        elif admin_choice == "3":
            self.generate_reports()
        elif admin_choice == "4":
            self.configure_system()
        elif admin_choice == "5":
            # View all employees
            self.view_all_employees()
            employee_choice = input("Enter employee ID to update/delete (or press Enter to go back): ")
            if employee_choice:
                self.update_or_delete_employee(employee_choice)
        elif admin_choice == "6":
            print("Returning to the main menu...\n ")
        else:
            print("Invalid choice. Please enter a valid option.\n ")
            
             
    def update_or_delete_employee(self, employee_id):
        action = input("Choose action: 'update' or 'delete': ").lower()
        if action == "update":
            self.update_employee_info(employee_id)
        elif action == "delete":
            self.delete_employee_account(employee_id)
        else:
            print("Invalid action!\n ")


    def monitor_transactions(self):
        print("Monitoring transactions...")
        for account_number, account in self.accounts.items():
            transactions = account.get_transaction_history()
            print(f"Transaction History for Account Number: {account_number}")
            for i, transaction in enumerate(transactions, start=1):
                print(f"{i}. {transaction}")
            print()

    def generate_reports(self):
        print("Generating reports...")
        # Report on account activity
        print("Account Activity Report:")
        for account_number, account in self.accounts.items():
            print(account.get_account_info())
        transactions = account.get_transaction_history()
        if transactions:
            for i, transaction in enumerate(transactions, start=1):
                print(f"{i}. {transaction}")
        else:
            print("No transactions recorded.")
        print()

        # Report on transaction volumes
        print("Transaction Volume Report:")
        for account_number, account in self.accounts.items():
            transactions = account.get_transaction_history()
            print(f"Account Number: {account_number}")
            print(f"Total Transactions: {len(transactions)}")
            print()

        # Report on financial performance
        print("Financial Performance Report: [Not Implemented]")
        print()

    def configure_system(self):
        print("Configuring system...")
        # For demonstration purposes, let's print a message indicating system configuration
        print("System configured successfully\n ")

    def get_transaction_history(self, account_number):
        account = self.accounts.get(account_number)
        if account:
            return account.get_transaction_history()
        return "Account not found!"
    
    def get_account_info(self, account_number):
        account = self.accounts.get(account_number)
        if account:
            return {
                'account_name': account.account_name,
                'account_number': account.account_number,
                'account_type': account.account_type,
                'balance': account.balance
            }
        return {"error": "Account not found!"}
    
    def loan_manager_menu(self):
        print("Loan Manager Menu:")
        print("1. Approve loan applications")
        print("2. Reject loan applications")
        print("3. View pending loan applications")
        print("4. Back to main menu\n ")

        choice = input("Enter your choice: ")
        if choice == "1":
            self.approve_loan_applications()
        elif choice == "2":
            self.reject_loan_applications()
        elif choice == "3":
            self.view_pending_loan_applications()
        elif choice == "4":
            print("Returning to the main menu...\n ")
        else:
            print("Invalid choice. Please enter a valid option.\n ")

    # Implement tasks for managing credit analyst accounts
    def credit_analyst_menu(self):
        print("Credit Analyst Menu:")
        print("1. Analyze credit scores")
        print("2. Review credit reports")
        print("3. Generate credit analysis reports")
        print("4. Back to main menu\n ")

        choice = input("Enter your choice: ")
        if choice == "1":
            self.analyze_credit_scores()
        elif choice == "2":
            self.review_credit_reports()
        elif choice == "3":
            self.generate_credit_analysis_reports()
        elif choice == "4":
            print("Returning to the main menu...\n ")
        else:
            print("Invalid choice. Please enter a valid option.\n ")

    # Implement tasks for managing bank teller accounts
    def bank_teller_menu(self):
        print("Bank Teller Menu:")
        print("1. Deposit money")
        print("2. Withdraw money")
        print("3. Transfer money")
        print("4. Check account balance")
        print("5. Back to main menu\n ")

        choice = input("Enter your choice: ")
        if choice == "1":
            self.deposit_money()
        elif choice == "2":
            self.withdraw_money()
        elif choice == "3":
            self.transfer_money()
        elif choice == "4":
            self.check_account_balance()
        elif choice == "5":
            print("Returning to the main menu...\n ")
        else:
            print("Invalid choice. Please enter a valid option.\n ")

    # Implement tasks for managing accountant accounts
    def accountant_menu(self):
        print("Accountant Menu:")
        print("1. Generate financial statements")
        print("2. Audit transactions")
        print("3. Calculate taxes")
        print("4. Back to main menu\n ")

        choice = input("Enter your choice: ")
        if choice == "1":
            self.generate_financial_statements()
        elif choice == "2":
            self.audit_transactions()
        elif choice == "3":
            self.calculate_taxes()
        elif choice == "4":
            print("Returning to the main menu...\n ")
        else:
            print("Invalid choice. Please enter a valid option.\n ")

# Define a class for the menu
class Menu:
    MENU = (
        ('Exit', 'exit'),
        ('Create a new account', 'create_account'),
        ('Log into an account', 'log_in'),
        ('Close an account', 'close_account'),
        ('Administrative Tasks', 'admin_tasks'),
    )

    def screen(self):
        prompt = '\n'.join(f'{i}. {name}' for i, (name, _) in enumerate(self.MENU)) + '\n'
        while True:
            choice = input(prompt)
            try:
                name, method = self.MENU[int(choice)]
                getattr(self, method)()
            except (ValueError, IndexError):
                print('Invalid choice')

    def exit(self):
        print('Goodbye!')
        exit()
            
        
    def _generate_account_number(self):
        while True:
            account_number = f'2000{random.randint(100000, 999999)}'
            if account_number not in self.accounts:
                return account_number


    def close_account(self):
        account_number = input("Enter the account number to close: ")
        bank.close_account(account_number)
        
    def log_in(self):
        account_number = input("Enter your account number: ")
        pin = getpass.getpass("Enter your PIN: ")
        if bank.log_in(account_number, pin):
            print("You have successfully logged in!\n ")
            self.account_menu(account_number)
        else:
            print("Login failed. Please check your account number and PIN.\n ")


class BankingSystem(Menu):
    def __init__(self):
        self.accounts: Dict[str, BankAccount] = {}
        super().__init__()  # Call the constructor of the parent class
        

    def create_account(self):
        account_name = input("Enter your full name: ")
        account_type = input("Enter account type (e.g., savings or current): ")
        initial_balance = float(input("Enter initial balance: "))
        personal_info = input("Enter personal info (e.g., married or single): ")
        pin = self._get_valid_pin()
        account_number = self._generate_account_number()
        account = BankAccount(account_name, account_number, account_type, initial_balance, personal_info, pin)
        self.accounts[account_number] = account
        print('Account created successfully!\n ')
        
    def _generate_account_number(self):
        while True:
            account_number = f'2000{random.randint(100000, 999999)}'
            if account_number not in self.accounts:
                return account_number
            
    def log_in(self):
            account_number = input("Enter your account number: ")
            pin = getpass.getpass("Enter your PIN: ")
            account = self.accounts.get(account_number)
            if account and account.pin == pin:
                    print("You have successfully logged in!\n ")
                    if account.account_type=="employee" :
                        employee_name = self.get_employee_name(account_number)
                        print(f"Welcome, {employee_name}!\n")
                    self.account_menu(account_number)  # Go to account menu based on user's position
            else:
                print("Login failed. Please check your account number and PIN.\n")

    def admin_tasks(self):
            print("\nAdministrative Tasks:")
            print("1. Managing employee accounts")
            print("2. Monitoring and auditing transactions")
            print("3. Generating reports")
            print("4. Configuring system parameters")
            print("5. Back to main menu\n ")

            admin_choice = input("Enter your choice: ")
            if admin_choice == "1":
                self.manage_employee_accounts()
            elif admin_choice == "2":
                bank.monitor_transactions()
            elif admin_choice == "3":
                bank.generate_reports()
            elif admin_choice == "4":
                bank.configure_system()
            elif admin_choice == "5":
                print("Returning to the main menu...\n ")
            else:
                print("Invalid choice. Please enter a valid option.\n ")
                
    def manage_employee_accounts(self):
        print("\nManaging Employee Accounts:")
        print("1. Create a new employee account")
        print("2. View all employee accounts")
        print("3. Update employee account information")
        print("4. Delete an employee account")
        print("5. Back to administrative tasks\n ")

        choice = input("Enter your choice: ")
        if choice == "1":
            self.create_employee_account()
        elif choice == "2":
            self.view_all_employees()
        elif choice == "3":
            employee_id = input("Enter employee ID: ")
            self.update_employee_info(employee_id)
        elif choice == "4":
            employee_id = input("Enter employee ID: ")
            self.delete_employee_account(employee_id)
        elif choice == "5":
            print("Returning to administrative tasks...\n ")
        else:
            print("Invalid choice. Please enter a valid option.\n ")

    def exit(self) -> bool:
        print('Bye!')
        return True

    MENU = (
        ('Exit', 'exit'),
        ('Create an account', 'create_account'),
        ('Log into an account', 'log_in'),
    )

# Function to print menu options
def print_options():
    print("What would you like to do?\n")
    print("1. Create a new account")
    print("2. Deposit money")
    print("3. Withdraw money")
    print("4. Transfer money")
    print("5. Log in")
    print("6. Check Balance")
    print("7. Get account information")
    print("8. View all accounts")
    print("9. Update account information")
    print("10. Contact Customer Care")
    print("11.Create an employee account")
    print("12.Login as an employee")
    print("13.Quit\n ")


# main program
def main_menu(bank):
    print("*********Welcome to CoBank***********")
    print("We're here to serve you. ")
    print()


# Create an instance of the Bank Management System
bank = BankManagementSystem()
# bank.employee_login()

while True:
    # Display menu options
    print_options()
    choice = input("Enter your choice: ")

    if choice == "1":
        # Create a new account
        bank.create_account()
      
    elif choice == "2":
        # Deposit money into an account
        account_number = input("Enter account number: ")
        amount = float(input("Enter amount to deposit: "))
        if bank.deposit(account_number, amount):
            print(f"You have successfully deposited #{amount} into your account!\n ")
        else:
            print("Account not found!!\n ")

    elif choice == "3":
        # Withdraw money from an account
        account_number = input("Enter account number: ")
        amount = float(input("Enter amount to withdraw: "))
        if bank.withdraw(account_number, amount):
            print("Withdrawal successful!!\n ")
        else:
            print("Sorry, you do not have sufficient funds in your account!!!\n ")

    elif choice == "4":
        # Transfer money between accounts
        sender_account_number = input("Enter sender's account number: ")
        recipient_account_number = input("Enter recipient's account number: ")
        amount = float(input("Enter amount to transfer: "))
        sender_pin = getpass.getpass("Enter sender's PIN: ")  # Prompt for sender's PIN
        if bank.transfer(sender_account_number, recipient_account_number, amount, sender_pin):
            print("Transfer successful!\n ")
        else:
            print("Transfer failed! Check account numbers or balances.\n ")
            
    elif choice == "5":
         # Log_in()
        account_number = input("Enter your account number: ")
        pin = getpass.getpass("Enter your PIN: ")
        if bank.log_in(account_number, pin):
            print("You have successfully logged in!\n ")
            # Proceed with account actions...
        while True:
            print("1. Deposit money")
            print("2. Withdraw money")
            print("3. Transfer money")
            print("4. Check balance")
            print("5. View transaction history")
            print("6. Logout")
            account_action = input("Enter your choice: ")
            if account_action == "1":
                amount = float(input("Enter the amount to deposit: "))
                if bank.deposit(account_number, amount):
                    print(f"You have successfully deposited #{amount} into your account.\n ")
                else:
                    print("Deposit failed! Please try again.\n ")
            elif account_action == "2":
                amount = float(input("Enter the amount to withdraw: "))
                if bank.withdraw(account_number, amount):
                    print(f"You have successfully withdrawn #{amount} from your account.\n ")
                else:
                    print("Withdrawal failed! Please check your balance and try again.\n ")
            elif account_action == "3":
                recipient_account_number = input("Enter the recipient's account number: ")
                amount = float(input("Enter the amount to transfer: "))
                sender_pin = getpass.getpass("Enter your PIN: ")
                if bank.transfer(account_number, recipient_account_number, amount, sender_pin):
                    print(f"Transfer of #{amount} to account {recipient_account_number} successful.\n ")
                else:
                    print("Transfer failed! Please check recipient's account number and your balance.\n ")
            elif account_action == "4":
                print(bank.get_account_info(account_number))
            elif account_action == "5":
                print("Transaction history:")
                print(bank.get_transaction_history(account_number))
            elif account_action == "6":
                print("Logging out...\n ")
                break
            else:
                print("Invalid choice! Please enter a number from 1 to 6.\n ")
        else:
            print("Login failed. Please check your account number and PIN.\n ")
            
            
    elif choice == "6":
        # Check balance
        account_number = input("Enter your account number: ")
        pin = getpass.getpass("Enter your PIN: ")
        if bank.log_in(account_number, pin):
            account_info = bank.get_account_info(account_number)
            print("Your current balance is:", account_info['balance'])
        else:
            print("Please check your account number and PIN.\n ")

    elif choice == "7":
        # Get account information
        account_number = input("Enter account number: ")
        print(bank.get_account_info(account_number))

    elif choice == "8":
        # View all accounts
        bank.view_all_accounts()

    elif choice == "9":
        # Update account information
        account_number = input("Enter account number: ")
        bank.update_account_info(account_number)

    elif choice == "10":
        # Contact Customer Care
        bank.customer_service()

    elif choice == "11":
        # Create an employee account
        bank.create_employee_account()
        
    elif choice == "12":
        # Log in as an employee
        bank.employee_login()  
        
    elif choice == "13":
        # Quit the program
        print("Thank you for banking with us Goodbye!")
        break

    else:
        print("Invalid choice! Kindly enter a number from 1 to 9.\n ")
