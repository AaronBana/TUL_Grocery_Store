import sqlite3
import json

class DataLayer:
    def __init__(self, db_name="Loyalty Card System.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._initialize_tables()

    def _initialize_tables(self):
        # Create Customer table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Customer (
                                    CustomerID INTEGER PRIMARY KEY AUTOINCREMENT,
                                    FirstName TEXT,
                                    LastName TEXT,
                                    Email TEXT,
                                    PhoneNumber TEXT,
                                    Address TEXT,
                                    CardNumber TEXT,
                                    IssueDate TEXT,
                                    ExpiryDate TEXT,
                                    TotalPoints INTEGER DEFAULT 0
                                )''')

        # Create Transactions table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Transactions (
                                    TransactionID INTEGER PRIMARY KEY AUTOINCREMENT,
                                    CustomerID INTEGER,
                                    TransactionDate TEXT,
                                    TotalAmount REAL,
                                    PointsEarned INTEGER,
                                    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID)
                                )''')

        # Create RewardRedemption table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS RewardRedemption (
                                    RedemptionID INTEGER PRIMARY KEY AUTOINCREMENT,
                                    CustomerID INTEGER,
                                    RewardID INTEGER,
                                    RedemptionDate TEXT,
                                    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID),
                                    FOREIGN KEY (RewardID) REFERENCES Reward(RewardID)
                                )''')

        # Create Reward table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Reward (
                                    RewardID INTEGER PRIMARY KEY AUTOINCREMENT,
                                    RewardName TEXT,
                                    Description TEXT,
                                    PointsRequired INTEGER
                                )''')
        self.conn.commit()

    def add_customer(self, first_name, last_name, email, phone_number, address, card_number, issue_date, expiry_date):
        self.cursor.execute('''INSERT INTO Customer (FirstName, LastName, Email, PhoneNumber, Address, CardNumber, IssueDate, ExpiryDate) 
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                            (first_name, last_name, email, phone_number, address, card_number, issue_date, expiry_date))
        self.conn.commit()

    def record_transaction(self, customer_id, transaction_date, total_amount, points_earned):
        self.cursor.execute('''INSERT INTO Transactions (CustomerID, TransactionDate, TotalAmount, PointsEarned) 
                                VALUES (?, ?, ?, ?)''', 
                            (customer_id, transaction_date, total_amount, points_earned))
        self.cursor.execute('''UPDATE Customer SET TotalPoints = TotalPoints + ? WHERE CustomerID = ?''', 
                            (points_earned, customer_id))
        self.conn.commit()

    def redeem_reward(self, customer_id, reward_id, redemption_date):
        reward = self.cursor.execute('''SELECT PointsRequired FROM Reward WHERE RewardID = ?''', (reward_id,)).fetchone()
        if not reward:
            raise ValueError("Reward not found.")
        
        required_points = reward[0]
        customer = self.cursor.execute('''SELECT TotalPoints FROM Customer WHERE CustomerID = ?''', (customer_id,)).fetchone()
        if not customer:
            raise ValueError("Customer not found.")

        current_points = customer[0]
        if current_points < required_points:
            raise ValueError("Insufficient points to redeem this reward.")

        self.cursor.execute('''INSERT INTO RewardRedemption (CustomerID, RewardID, RedemptionDate) 
                                VALUES (?, ?, ?)''', 
                            (customer_id, reward_id, redemption_date))
        self.cursor.execute('''UPDATE Customer SET TotalPoints = TotalPoints - ? WHERE CustomerID = ?''', 
                            (required_points, customer_id))
        self.conn.commit()

    def add_reward(self, reward_name, description, points_required):
        self.cursor.execute('''INSERT INTO Reward (RewardName, Description, PointsRequired) 
                                VALUES (?, ?, ?)''', 
                            (reward_name, description, points_required))
        self.conn.commit()

    def export_data_to_json(self, table_name, file_name):
        self.cursor.execute(f"SELECT * FROM {table_name}")
        rows = self.cursor.fetchall()
        
        # Get column names
        columns = [description[0] for description in self.cursor.description]
        
        # Convert rows to dictionary format
        data = [dict(zip(columns, row)) for row in rows]
        
        # Write to JSON file
        with open(file_name, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        
        print(f"Data from {table_name} exported to {file_name} successfully.")

    def close(self):
        self.conn.close()


class BusinessLogicLayer:
    def __init__(self, data_layer):
        self.data_layer = data_layer

    def add_customer(self, first_name, last_name, email, phone_number, address, card_number, issue_date, expiry_date):
        self.data_layer.add_customer(first_name, last_name, email, phone_number, address, card_number, issue_date, expiry_date)

    def record_transaction(self, customer_id, transaction_date, total_amount):
        points_earned = int(total_amount // 1)  # Example: 1 point for every £1 spent
        self.data_layer.record_transaction(customer_id, transaction_date, total_amount, points_earned)

    def redeem_reward(self, customer_id, reward_id, redemption_date):
        self.data_layer.redeem_reward(customer_id, reward_id, redemption_date)

    def add_reward(self, reward_name, description, points_required):
        self.data_layer.add_reward(reward_name, description, points_required)


class PresentationLayer:
    def __init__(self, business_logic_layer):
        self.bl_layer = business_logic_layer

    def show_menu(self):
        while True:
            print("\n1. Add Customer")
            print("2. Record Transaction")
            print("3. Redeem Reward")
            print("4. Add Reward")
            print("5. Export Data to JSON")
            print("6. Exit")
            choice = input("Choose an option: ")

            if choice == '1':
                self.add_customer_ui()
            elif choice == '2':
                self.record_transaction_ui()
            elif choice == '3':
                self.redeem_reward_ui()
            elif choice == '4':
                self.add_reward_ui()
            elif choice == '5':
                self.export_data_ui()
            elif choice == '6':
                print("Exit. Sign Off.")
                break
            else:
                print("Invalid choice. Please try again.")

    def add_customer_ui(self):
        first_name = input("Enter first name: ")
        last_name = input("Enter last name: ")
        email = input("Enter email: ")
        phone_number = input("Enter phone number: ")
        address = input("Enter address: ")
        card_number = input("Enter card number: ")
        issue_date = input("Enter card issue date (DD/MM/YYYY): ")
        expiry_date = input("Enter card expiry date (DD/MM/YYYY): ")

        self.bl_layer.add_customer(first_name, last_name, email, phone_number, address, card_number, issue_date, expiry_date)
        print("Customer added successfully.")

    def record_transaction_ui(self):
        customer_id = int(input("Enter customer ID: "))
        transaction_date = input("Enter transaction date (DD/MM/YYYY): ")
        total_amount = float(input("Enter total amount: "))

        self.bl_layer.record_transaction(customer_id, transaction_date, total_amount)
        print("Transaction recorded successfully.")

    def redeem_reward_ui(self):
        customer_id = int(input("Enter customer ID: "))
        reward_id = int(input("Enter reward ID: "))
        redemption_date = input("Enter redemption date (DD/MM/YYYY): ")

        try:
            self.bl_layer.redeem_reward(customer_id, reward_id, redemption_date)
            print("Reward redeemed successfully.")
        except ValueError as e:
            print(f"Error: {e}")

    def add_reward_ui(self):
        reward_name = input("Enter reward name: ")
        description = input("Enter reward description: ")
        points_required = int(input("Enter points required to redeem: "))

        self.bl_layer.add_reward(reward_name, description, points_required)
        print("Reward added successfully.")

    def export_data_ui(self):
        table_name = input("Enter the table name you want to export: (Customer, Transactions, Reward, RewardRedemption): ")
        file_name = input(f"Enter the filename to save {table_name} data (e.g., {table_name}.json): ")
        self.bl_layer.data_layer.export_data_to_json(table_name, file_name)


if __name__ == "__main__":
    # Initialize the data layer
    data_layer = DataLayer()

    # Initialize the business logic layer with the data layer
    bl_layer = BusinessLogicLayer(data_layer)

    # Initialize the presentation layer with the business logic layer
    ui_layer = PresentationLayer(bl_layer)

    # Start the application
    ui_layer.show_menu()

    # Close database connection on exit
    data_layer.close()
