import sqlite3
import json

class InventorySystem:
    def __init__(self, db_file="Inventory System.db"):
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
            # Convert the product data to a list of dictionaries
            data = [{"product_id": p[0], "name": p[1], "price": p[2], "quantity": p[3]} for p in products]
            
            # Write to a JSON file
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
                cursor.execute("INSERT INTO categories (name) VALUES ('Dairy')")
                cursor.execute("INSERT INTO categories (name) VALUES ('Snacks')")
                cursor.execute("INSERT INTO categories (name) VALUES ('Beverages')")
                
                # Sample products
                self.add_product("1", "Milk", 1.50, 15, 1)  # Category 1 (Dairy)
                self.add_product("2", "Bread", 1.00, 15, 2)  # Category 2 (Snacks)
                self.add_product("3", "Eggs", 2.50, 10, 1)  # Category 1 (Dairy)
                self.add_product("4", "Butter", 2.00, 10, 1)  # Category 1 (Dairy)
                self.add_product("5", "Chocolate Bar", 0.75, 25, 2)  # Category 2 (Snacks)
                self.add_product("6", "Crisps", 1.25, 30, 2)  # Category 2 (Snacks)
                self.add_product("7", "Soda Can", 1.00, 40, 3)  # Category 3 (Beverages)
                self.add_product("8", "Toothpaste", 3.00, 25, 1)  # Category 1 (Dairy)
                self.add_product("9", "Shampoo", 4.50, 10, 1)  # Category 1 (Dairy)
                self.add_product("10", "Packet of Biscuits", 2.00, 20, 2)  # Category 2 (Snacks)
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

# Main program to interact with the inventory system
if __name__ == "__main__":
    inventory_system = InventorySystem()

    while True:
        print("\nInventory System Menu:")
        print("1. View Inventory")
        print("2. Add Product")
        print("3. Update Product Quantity")
        print("4. Export Inventory to JSON")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            products = inventory_system.display_inventory()
            print("\nCurrent Inventory:")
            for product in products:
                print(f"ID: {product[0]}, Name: {product[1]}, Price: £{product[2]:.2f}, Quantity: {product[3]}")
        elif choice == "2":
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
        elif choice == "3":
            product_id = input("Enter Product ID to update: ")
            try:
                quantity_purchased = int(input("Enter Quantity to subtract: "))
                inventory_system.update_quantity(product_id, quantity_purchased)
                print("Product quantity updated successfully.")
            except ValueError:
                print("Invalid quantity. Please enter a valid number.")
        elif choice == "4":
            file_name = input("Enter the filename for JSON export (e.g., Inventory.json): ") or "inventory.json"
            inventory_system.export_to_json(file_name)
        elif choice == "5":
            inventory_system.close_connection()
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
