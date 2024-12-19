# Component 2; System Design Document & Prototype
# Grocery Store Python Code
# By Anas Karoo, Aaron Banahene, & Marcello Gold

import sqlite3
import json

print("")
print("WELCOME TO THE GROCERY STORE!")
print("Start by selecting an option from the Main Menu!")

# INVENTORY SYSTEM
class InventorySystem:
    def __init__(self, db_file="InventorySystem.db"):
        """Initialize the Inventory System and connect to the database."""
        self.db_file = db_file
        self.conn = sqlite3.connect(self.db_file)
        self.create_tables()  # Create all necessary tables
        self.initialize_products()

    def create_tables(self):
        """Create all necessary tables in the database."""
        try:
            cursor = self.conn.cursor()

            # Create Categories Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL
                )
            """)

            # Create Inventory Table with a foreign key to Categories Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inventory (
                    product_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    quantity INTEGER NOT NULL,
                    category_id INTEGER,
                    FOREIGN KEY (category_id) REFERENCES categories(category_id)
                )
            """)

            # Create Sales Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sales (
                    sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sale_date TEXT NOT NULL,
                    total_amount REAL NOT NULL
                )
            """)

            # Create Sales_Items Table, linking Sales and Inventory
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sales_items (
                    sales_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sale_id INTEGER,
                    product_id TEXT,
                    quantity INTEGER NOT NULL,
                    price REAL NOT NULL,
                    FOREIGN KEY (sale_id) REFERENCES sales(sale_id),
                    FOREIGN KEY (product_id) REFERENCES inventory(product_id)
                )
            """)

            self.conn.commit()
        except Exception as e:
            print(f"Error creating tables: {e}")

    def get_all_products(self):
        """Fetch all products from the inventory."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT product_id, name, price, quantity FROM inventory")
            products = cursor.fetchall()
            return products
        except Exception as e:
            print(f"Error getting all products: {e}")
            return []

    def export_to_json(self, file_name="inventory_data.json"):
        """Export inventory data to a JSON file."""
        try:
            products = self.get_all_products()
            data = [{"product_id": p[0], "name": p[1], "price": p[2], "quantity": p[3]} for p in products]
            with open(file_name, "w") as json_file:
                json.dump(data, json_file, indent=4)
            print(f"Inventory data exported successfully to {file_name}.")
        except Exception as e:
            print(f"Error exporting to JSON: {e}")

    def get_product_details(self, product_id):
        """Fetch details of a single product by its ID."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT product_id, name, price, quantity FROM inventory WHERE product_id = ?", (product_id,))
            result = cursor.fetchone()
            if result:
                return {
                    "product_id": result[0],
                    "name": result[1],
                    "price": result[2],
                    "quantity": result[3]
                }
            return None  # Product not found
        except Exception as e:
            print(f"Error fetching product details: {e}")
            return None

    def initialize_products(self):
        """Initialize the database with some sample products if it's empty."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM inventory")
            if cursor.fetchone()[0] == 0:
                # Sample categories
                cursor.execute("INSERT INTO categories (name) VALUES ('Dairy')")                    # CategoryID: 1
                cursor.execute("INSERT INTO categories (name) VALUES ('Snacks')")                   # CategoryID: 2
                cursor.execute("INSERT INTO categories (name) VALUES ('Beverages')")                # CategoryID: 3
                cursor.execute("INSERT INTO categories (name) VALUES ('Bakery')")                   # CategoryID: 4
                cursor.execute("INSERT INTO categories (name) VALUES ('Fruit & Veg.')")             # CategoryID: 5
                cursor.execute("INSERT INTO categories (name) VALUES ('Frozen Foods')")             # CategoryID: 6
                cursor.execute("INSERT INTO categories (name) VALUES ('Toiletries & Beauty')")      # CategoryID: 7
                cursor.execute("INSERT INTO categories (name) VALUES ('Home & Entertainment')")     # CategoryID: 8
                cursor.execute("INSERT INTO categories (name) VALUES ('Clothing')")                 # CategoryID: 9
                cursor.execute("INSERT INTO categories (name) VALUES ('Other')")                    # CategoryID: 10
                
                # Sample products
                self.add_product("1", "Milk", 1.50, 25, 1)  # Category 1 (Dairy)
                self.add_product("2", "Bread", 1.00, 25, 2)  # Category 4 (Bakery)
                self.add_product("3", "Eggs", 2.50, 20, 1)  # Category 10 (Other)
                self.add_product("4", "Butter", 2.00, 30, 1)  # Category 1 (Dairy)
                self.add_product("5", "Chocolate Bar", 0.75, 45, 2)  # Category 2 (Snacks)
                self.add_product("6", "Crisps", 1.25, 45, 2)  # Category 2 (Snacks)
                self.add_product("7", "Soda Can", 1.00, 45, 3)  # Category 3 (Beverages)
                self.add_product("8", "Toothpaste", 3.00, 50, 1)  # Category 7 (Toiletries & Beauty)
                self.add_product("9", "Shampoo", 4.50, 40, 1)  # Category 7 (Toiletries & Beauty)
                self.add_product("10", "Packet of Biscuits", 2.00, 30, 2)  # Category 2 (Snacks)
                self.conn.commit()
        except Exception as e:
            print(f"Error initializing products: {e}")

    def add_product(self, product_id, name, price, quantity, category_id):
        """Add a product to the inventory."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO inventory (product_id, name, price, quantity, category_id) VALUES (?, ?, ?, ?, ?)",
                           (product_id, name, price, quantity, category_id))
            self.conn.commit()
        except Exception as e:
            print(f"Error adding product: {e}")

    def display_inventory(self):
        """Return the list of all products in the inventory."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT product_id, name, price, quantity FROM inventory")
            products = cursor.fetchall()
            return products
        except Exception as e:
            print(f"Error displaying inventory: {e}")
            return []

    def update_quantity(self, product_id, quantity_purchased):
        """Update the quantity of a product after purchase."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE inventory SET quantity = quantity - ? WHERE product_id = ?",
                           (quantity_purchased, product_id))
            self.conn.commit()
        except Exception as e:
            print(f"Error updating quantity: {e}")

    def close_connection(self):
        """Close the database connection."""
        self.conn.close()

# CHECKOUT SYSTEM
class CheckoutSystem:
    def __init__(self, inventory_system, bl_layer):  # Accept bl_layer in the constructor
        self.cart = []
        self.inventory_system = inventory_system  # Initialize InventorySystem
        self.bl_layer = bl_layer  # Store the BusinessLogicLayer instance
        self.total = 0.0

    def login(self):
        """Allow a staff member to log in."""
        print("\n--- STAFF LOGIN ---")
        username = input("Enter your username: ").strip()
        password = input("Enter your password: ").strip()
        # For simplicity, we will allow any username/password
        print(f"\nWelcome, {username}! You are now logged in!")

    def display_inventory(self):
        """Display all available products to the user."""
        print("\nAvailable Products:")
        products = self.inventory_system.get_all_products()
        if not products:
            print("No products available in the inventory.")
            return

        # Displaying the products
        for product in products:
            product_id, name, price, quantity = product
            print(f"ID: {product_id}, Name: {name}, Price: £{price:.2f}, Quantity: {quantity}")

    def display_cart(self):
        """Display the items in the cart."""
        if not self.cart:
            print("\nYour cart is empty!")
            return

        print("\nYour Cart:")
        print("{:<10} {:<25} {:<10} {:<10}".format("ID", "Name", "Price(£)", "Quantity"))
        print("-" * 60)
        for product_id, name, quantity, price in self.cart:
            print("{:<10} {:<25} {:<10.2f} {:<10}".format(product_id, name, price, quantity))
        print("-" * 60)
        print(f"Total: £{self.total:.2f}")

    def checkout(self):
        """Complete the purchase."""
        print("\nChecking out...\n")
        self.display_cart()

        if not self.cart:
            print("Your cart is empty! Cannot proceed with checkout and payment!")
            print("Thank you for visiting our Grocery Store. See you again soon!")
            return

        # Ask if the customer has a loyalty card
        has_loyalty_card = input("Do you have a Loyalty Card? (Yes/No): ").strip().lower()
        
        total_amount = self.total
        points_earned = int(total_amount // 1)  # Example: 1 point for every £1 spent
        
        if has_loyalty_card == 'yes':
            # Here you would normally add points to the customer's loyalty card
            customer_id = int(input("Enter Customer ID: "))
            self.bl_layer.record_transaction(customer_id, "transaction_date_placeholder", total_amount)
            print(f"{points_earned} Loyalty Point(s) earned on your shopping.")

        payment_method = input("Select Payment Type (Cash or Card): ").strip().lower()
        if payment_method == "cash":
            try:
                amount_given = float(input("Enter money amount given: £"))
                if amount_given < total_amount:
                    print("Insufficient amount provided! Transaction failed!")
                    return
                change = amount_given - total_amount
                print(f"Payment successful! Total: £{total_amount:.2f}, Change: £{change:.2f}")
            except ValueError:
                print("Invalid input. Please enter a numeric value.")
                return
        elif payment_method == "card":
            print(f"Payment successful! Total: £{total_amount:.2f}")
        else:
            print("Invalid payment method!")
            return

        self.export_cart_to_json(total_amount, points_earned)
        self.print_receipt(total_amount, points_earned)
        self.cart.clear()  # Clear cart after purchase
        self.total = 0.0

    def export_cart_to_json(self, total_amount, points_earned):
        """Export cart details to a JSON file."""
        transaction_data = {
            "cart": [
                {
                    "product_id": product_id,
                    "name": name,
                    "quantity": quantity,
                    "price": price
                } for product_id, name, quantity, price in self.cart
            ],
            "subtotal": self.total,
            "total_amount": total_amount,
            "points_earned": points_earned
        }

        try:
            with open("Transaction.json", "w") as json_file:
                json.dump(transaction_data, json_file, indent=4)
            print("Transaction details have been exported to 'Transaction.json'.")
        except IOError:
            print("Failed to export transaction details to JSON.")

    def print_receipt(self, total_amount, points_earned):
        """Print the receipt for the transaction."""
        print("\n--- Receipt ---")
        print("{:<10} {:<25} {:<10} {:<10}".format("ID", "Name", "Price(£)", "Quantity"))
        print("-" * 60)
        for product_id, name, quantity, price in self.cart:
            print("{:<10} {:<25} {:<10.2f} {:<10}".format(product_id, name, price, quantity))
        print("-" * 60)
        print(f"Total: £{total_amount:.2f}")
        print(f"Points Earned: {points_earned}")
        print("Thank you for shopping with us! See you again soon!")

# LOYALTY CARD SYSTEM
class DataLayer:
    def __init__(self, db_name="LoyaltyCardSystem.db"):
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

# MAIN MENU
def main():
    inventory_system = InventorySystem()
    data_layer = DataLayer()
    bl_layer = BusinessLogicLayer(data_layer)
    checkout_system = CheckoutSystem(inventory_system, bl_layer)  # Pass bl_layer here

    while True:
        print("\nMAIN MENU:")
        print("1. Inventory System")
        print("2. Checkout System")
        print("3. Loyalty Card System")
        print("4. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            while True:
                print("\nINVENTORY SYSTEM MENU:")
                print("1. View Inventory")
                print("2. Add Product")
                print("3. Update Product Quantity")
                print("4. Export Inventory to JSON")
                print("5. Back to Main Menu")
                inv_choice = input("Choose an option: ")

                if inv_choice == "1":
                    products = inventory_system.display_inventory()
                    print("\nCurrent Inventory:")
                    for product in products:
                        print(f"ID: {product[0]}, Name: {product[1]}, Price: £{product[2]:.2f}, Quantity: {product[3]}")
                elif inv_choice == "2":
                    product_id = input("Enter Product ID: ")
                    name = input("Enter Product Name: ")
                    try:
                        price = float(input("Enter Product Price: "))
                        quantity = int(input("Enter Product Quantity: "))
                        category_id = int(input("Enter Category ID: "))  # Category ID
                        inventory_system.add_product(product_id, name, price, quantity, category_id)
                        print("Product added successfully.")
                    except ValueError:
                        print("Invalid price or quantity. Please enter valid numeric values.")
                elif inv_choice == "3":
                    product_id = input("Enter Product ID to update: ")
                    try:
                        quantity_purchased = int(input("Enter Quantity to subtract: "))
                        inventory_system.update_quantity(product_id, quantity_purchased)
                        print("Product quantity updated successfully.")
                    except ValueError:
                        print("Invalid quantity. Please enter a valid number.")
                elif inv_choice == "4":
                    file_name = input("Enter the filename for JSON export (e.g., Inventory.json): ") or "inventory.json"
                    inventory_system.export_to_json(file_name)
                elif inv_choice == "5":
                    break
                else:
                    print("Invalid option! Please try again!")

        elif choice == "2":
            checkout_system.login()  # Call the login method here
            while True:
                checkout_system.display_inventory()
                print("\nCHECKOUT SYSTEM MENU: ")
                print("1. Add an item to the cart")
                print("2. Remove/Edit an item in the cart")
                print("3. View cart")
                print("4. Proceed to checkout")
                print("5. Back to Main Menu")
                co_choice = input("Choose an option: ").strip()

                if co_choice == "1":
                    product_id = input("\nEnter the product ID: ").strip()
                    product = checkout_system.inventory_system.get_product_details(product_id)
                    if not product:
                        print("Invalid product ID, please try again.")
                        continue

                    try:
                        quantity = int(input(f"Enter the quantity for {product['name']}: ").strip())
                        if quantity <= 0:
                            print("Please enter a positive quantity.")
                            continue
                    except ValueError:
                        print("Invalid input. Please enter a valid quantity.")
                        continue

                    if quantity > product['quantity']:
                        print(f"Insufficient stock for {product['name']}. Only {product['quantity']} available.")
                        continue

                    checkout_system.cart.append((product_id, product['name'], quantity, product['price']))
                    checkout_system.total += product['price'] * quantity
                    print(f"Added {quantity} x {product['name']} to your cart.")

                    # Ensure quantity decreases correctly
                    checkout_system.inventory_system.update_quantity(product_id, quantity)

                elif co_choice == "2":
                    checkout_system.display_cart()
                    product_id = input("Enter the product ID to edit/remove: ").strip()
                    item = next((item for item in checkout_system.cart if item[0] == product_id), None)

                    if not item:
                        print("Item not found in the cart.")
                        continue

                    print("Options:")
                    print("1. Remove item")
                    print("2. Edit quantity")
                    edit_choice = input("Choose an option: ").strip()

                    if edit_choice == "1":
                        checkout_system.cart.remove(item)
                        checkout_system.total -= item[2] * item[3]
                        checkout_system.inventory_system.update_quantity(product_id, item[2])
                        print(f"Removed {item[1]} from the cart.")

                    elif edit_choice == "2":
                        try:
                            new_quantity = int(input(f"Enter new quantity for {item[1]}: ").strip())
                            if new_quantity <= 0:
                                print("Quantity must be greater than zero.")
                                continue

                            difference = new_quantity - item[2]
                            if difference > 0 and difference > checkout_system.inventory_system.get_product_details(product_id)['quantity']:
                                print(f"Insufficient stock! Unable to update quantity!")
                                continue

                            item_index = checkout_system.cart.index(item)
                            checkout_system.cart[item_index] = (item[0], item[1], new_quantity, item[3])
                            checkout_system.total += difference * item[3]
                            checkout_system.inventory_system.update_quantity(product_id, difference)
                            print(f"Updated {item[1]} to quantity {new_quantity}.")

                        except ValueError:
                            print("Invalid input! Please enter a valid quantity!")

                elif co_choice == "3":
                    # View the cart
                    checkout_system.display_cart()

                elif co_choice == "4":
                    checkout_system.checkout()
                    break  # Proceed to checkout

                elif co_choice == "5":
                    # Exit the program or cancel the cart
                    print("Exiting Cart Management...")
                    print("Thank you! Exit Successful! Signing Off!")
                    checkout_system.cart.clear()
                    checkout_system.total = 0.0
                    break

                else:
                    print("Invalid option! Please try again!")

        elif choice == "3":
            while True:
                print("\nLOYALTY CARD SYSTEM MENU:")
                print("1. Add Customer")
                print("2. Record Transaction")
                print("3. Redeem Reward")
                print("4. Add Reward")
                print("5. Export Data to JSON")
                print("6. Back to Main Menu")
                lc_choice = input("Choose an option: ")

                if lc_choice == '1':
                    first_name = input("Enter first name: ")
                    last_name = input("Enter last name: ")
                    email = input("Enter email: ")
                    phone_number = input("Enter phone number: ")
                    address = input("Enter address: ")
                    card_number = input("Enter card number: ")
                    issue_date = input("Enter card issue date (DD/MM/YYYY): ")
                    expiry_date = input("Enter card expiry date (DD/MM/YYYY): ")

                    bl_layer.add_customer(first_name, last_name, email, phone_number, address, card_number, issue_date, expiry_date)
                    print("Customer added successfully.")

                elif lc_choice == '2':
                    customer_id = int(input("Enter customer ID: "))
                    transaction_date = input("Enter transaction date (DD/MM/YYYY): ")
                    total_amount = float(input("Enter total amount: "))

                    bl_layer.record_transaction(customer_id, transaction_date, total_amount)
                    print("Transaction recorded successfully.")

                elif lc_choice == '3':
                    customer_id = int(input("Enter customer ID: "))
                    reward_id = int(input("Enter reward ID: "))
                    redemption_date = input("Enter redemption date (DD/MM/YYYY): ")

                    try:
                        bl_layer.redeem_reward(customer_id, reward_id, redemption_date)
                        print("Reward redeemed successfully.")
                    except ValueError as e:
                        print(f"Error: {e}")

                elif lc_choice == '4':
                    reward_name = input("Enter reward name: ")
                    description = input("Enter reward description: ")
                    points_required = int(input("Enter points required to redeem: "))

                    bl_layer.add_reward(reward_name, description, points_required)
                    print("Reward added successfully.")

                elif lc_choice == '5':
                    table_name = input("Enter the table name you want to export (Customer, Transactions, Reward, RewardRedemption): ")
                    file_name = input(f"Enter the filename to save {table_name} data (e.g., {table_name}.json): ")
                    bl_layer.data_layer.export_data_to_json(table_name, file_name)

                elif lc_choice == '6':
                    break
                else:
                    print("Invalid option! Please try again!")

        elif choice == "4":
            print("Exiting the Grocery Store System...")
            print("Thank you! Exit Successful! Signing Off!")
            print("See you again soon!")
            break
        else:
            print("Invalid option! Please try again!")

if __name__ == "__main__":
    main()
