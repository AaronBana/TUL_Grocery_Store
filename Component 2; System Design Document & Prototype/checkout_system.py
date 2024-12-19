import sqlite3
import json
from inventory_system import InventorySystem

class CheckoutSystem:
    def __init__(self):
        self.cart = []
        self.inventory_system = InventorySystem()  # Initialize InventorySystem
        self.total = 0.0
        self.tax_rate = 0.1  # Example tax rate (10%)

    def login(self):
        """Allow a staff member to log in."""
        print("\n--- Staff Login ---")
        username = input("Enter your username: ").strip()
        password = input("Enter your password: ").strip()
        print(f"\nWelcome, {username}! You are now logged in.")

    def display_inventory(self):
        """Display all available products to the user."""
        print("\nAvailable Products:")
        products = self.inventory_system.get_all_products()  # Get all products
        if not products:
            print("No products available in the inventory.")
            return

        # Displaying the products
        for product in products:
            product_id, name, price, quantity = product
            print(f"ID: {product_id}, Name: {name}, Price: £{price}, Quantity: {quantity}")

    def add_to_cart(self):
        """Manage the cart: add, remove, or edit items."""
        while True:
            # Display inventory
            self.display_inventory()

            print("\nOptions: ")
            print("1. Add an item to the cart")
            print("2. Remove/Edit an item in the cart")
            print("3. View cart")
            print("4. Proceed to checkout")
            print("5. Exit")
            choice = input("Enter your choice: ").strip()

            if choice == "1":
                # Add an item to the cart
                product_id = input("\nEnter the product ID: ").strip()
                product = self.inventory_system.get_product_details(product_id)
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

                self.cart.append((product_id, product['name'], quantity, product['price']))
                self.total += product['price'] * quantity
                print(f"Added {quantity} x {product['name']} to your cart.")

                # Ensure quantity decreases correctly
                self.inventory_system.update_quantity(product_id, -quantity)

            elif choice == "2":
                # Remove or edit an item in the cart
                self.display_cart()
                product_id = input("Enter the product ID to edit/remove: ").strip()
                item = next((item for item in self.cart if item[0] == product_id), None)

                if not item:
                    print("Item not found in the cart.")
                    continue

                print("Options:")
                print("1. Remove item")
                print("2. Edit quantity")
                edit_choice = input("Enter your choice: ").strip()

                if edit_choice == "1":
                    self.cart.remove(item)
                    self.total -= item[2] * item[3]
                    self.inventory_system.update_quantity(product_id, item[2])
                    print(f"Removed {item[1]} from the cart.")

                elif edit_choice == "2":
                    try:
                        new_quantity = int(input(f"Enter new quantity for {item[1]}: ").strip())
                        if new_quantity <= 0:
                            print("Quantity must be greater than zero.")
                            continue

                        difference = new_quantity - item[2]
                        if difference > 0 and difference > self.inventory_system.get_product_details(product_id)['quantity']:
                            print(f"Insufficient stock. Unable to update quantity.")
                            continue

                        item_index = self.cart.index(item)
                        self.cart[item_index] = (item[0], item[1], new_quantity, item[3])
                        self.total += difference * item[3]
                        self.inventory_system.update_quantity(product_id, -difference)
                        print(f"Updated {item[1]} to quantity {new_quantity}.")

                    except ValueError:
                        print("Invalid input. Please enter a valid quantity.")

            elif choice == "3":
                # View the cart
                self.display_cart()

            elif choice == "4":
                # Proceed to checkout
                break

            elif choice == "5":
                # Exit the program or cancel the cart
                print("Exiting cart management...")
                self.cart.clear()
                self.total = 0.0
                break

            else:
                print("Invalid choice. Please try again.")

    def display_cart(self):
        """Display the items in the cart."""
        if not self.cart:
            print("\nYour cart is empty.")
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
            print("Your cart is empty. Cannot proceed with checkout.")
            return

        total_with_tax = self.total * (1 + self.tax_rate)
        print(f"Total with tax (10%): £{total_with_tax:.2f}")

        payment_method = input("Select payment method (cash, card): ").strip().lower()
        if payment_method in ["cash", "card"]:
            print(f"Payment successful! Total: £{total_with_tax:.2f}")
            self.export_cart_to_json(total_with_tax)
            self.print_receipt(total_with_tax)
            self.cart.clear()  # Clear cart after purchase
            self.total = 0.0
        else:
            print("Invalid payment method.")

    def export_cart_to_json(self, total_with_tax):
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
            "tax": self.total * self.tax_rate,
            "total_with_tax": total_with_tax
        }

        try:
            with open("Transaction.json", "w") as json_file:
                json.dump(transaction_data, json_file, indent=4)
            print("Transaction details have been exported to 'Transaction.json'.")
        except IOError:
            print("Failed to export transaction details to JSON.")

    def print_receipt(self, total_with_tax):
        """Print the receipt for the transaction."""
        print("\n--- Receipt ---")
        print("{:<10} {:<25} {:<10} {:<10}".format("ID", "Name", "Price(£)", "Quantity"))
        print("-" * 60)
        for product_id, name, quantity, price in self.cart:
            print("{:<10} {:<25} {:<10.2f} {:<10}".format(product_id, name, price, quantity))
        print("-" * 60)
        print(f"Subtotal: £{self.total:.2f}")
        print(f"Tax: £{self.total * self.tax_rate:.2f}")
        print(f"Total: £{total_with_tax:.2f}")
        print("Thank you for shopping with us!")

# Example usage
if __name__ == "__main__":
    checkout = CheckoutSystem()

    # Log in staff member
    checkout.login()

    # Allow customer to add items to cart
    checkout.add_to_cart()

    # Checkout
    checkout.checkout()
