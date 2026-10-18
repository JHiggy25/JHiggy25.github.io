from LoginActivity import Login

def display_inventory(login_system):
    """Display all inventory records."""
    try:
        items = login_system.database.get_all_items()

        if not items:
            print("\nYour inventory is empty.")
            return

        print("\n" + "=" * 75)
        print(f"{'ID':<6}{'Item Name':<30}{'Quantity':<15}{'Low-Stock At':<15}")
        print("=" * 75)

        for item in items:
            print(
                f"{item['id']:<6}"
                f"{item['itemName']:<30}"
                f"{item['quantity']:<15}"
                f"{item['low_stock_threshold']:<15}"
            )

        print("=" * 75)

    except Exception as exc:
        print(f"Unable to retrieve inventory: {exc}")


def display_stock_alerts(login_system):
    """Display low-stock and out-of-stock notifications."""
    try:
        out_of_stock = (
            login_system.database.get_out_of_stock_items()
        )
        low_stock = login_system.database.get_low_stock_items()

        print("\n--- Inventory Stock Alerts ---")

        if out_of_stock:
            print("\nOUT OF STOCK:")
            for item in out_of_stock:
                print(f"  - {item['itemName']} (quantity: 0)")

        # Avoid listing zero-quantity items a second time.
        low_stock = [
            item for item in low_stock
            if item["quantity"] > 0
        ]

        if low_stock:
            print("\nLOW STOCK:")
            for item in low_stock:
                print(
                    f"  - {item['itemName']}: "
                    f"{item['quantity']} remaining "
                    f"(alert threshold: {item['low_stock_threshold']})"
                )

        if not out_of_stock and not low_stock:
            print("All inventory items are adequately stocked.")

    except Exception as exc:
        print(f"Unable to retrieve stock alerts: {exc}")


def add_inventory_item(login_system):
    """Prompt the user to add an inventory item."""
    print("\n--- Add Inventory Item ---")

    item_name = input("Enter item name: ").strip()

    if not item_name:
        print("Item name cannot be empty.")
        return

    quantity = get_nonnegative_integer("Enter starting quantity: ")
    if quantity is None:
        return

    threshold = get_nonnegative_integer(
        "Enter low-stock alert threshold (default 3): ",
        default=3,
    )
    if threshold is None:
        return

    try:
        added = login_system.database.add_item(
            item_name,
            quantity,
            threshold,
        )

        if added:
            print(f"'{item_name}' added successfully.")
            if quantity == 0:
                print("Alert: this item is currently out of stock.")
            elif quantity <= threshold:
                print("Alert: this item is at or below its stock threshold.")
        else:
            print(
                "Could not add the item. It may already exist "
                "or the input may be invalid."
            )

    except Exception as exc:
        print(f"Unable to add inventory item: {exc}")


def update_inventory_item(login_system):
    """Update an item's quantity, including setting it to zero."""
    print("\n--- Update Inventory Quantity ---")

    item_name = input("Enter the exact item name: ").strip()

    if not item_name:
        print("Item name cannot be empty.")
        return

    try:
        existing = login_system.database.get_item(item_name)

        if existing is None:
            print("Item not found.")
            return

        print(f"Current quantity: {existing['quantity']}")
        print("Enter 0 if the item is sold out.")

        quantity = get_nonnegative_integer("Enter new quantity: ")
        if quantity is None:
            return

        updated = login_system.database.update_item(
            item_name,
            quantity,
        )

        if updated:
            print(f"Quantity for '{item_name}' updated to {quantity}.")

            if quantity == 0:
                print("OUT OF STOCK: Replenishment is needed.")
            elif quantity <= existing["low_stock_threshold"]:
                print("LOW STOCK: Consider replenishing this item.")
        else:
            print("The quantity was not changed.")

    except Exception as exc:
        print(f"Unable to update inventory item: {exc}")


def change_stock_threshold(login_system):
    """Allow the user to change an item's low-stock threshold."""
    print("\n--- Change Low-Stock Threshold ---")

    item_name = input("Enter the exact item name: ").strip()

    if not item_name:
        print("Item name cannot be empty.")
        return

    threshold = get_nonnegative_integer("Enter the new threshold: ")
    if threshold is None:
        return

    try:
        updated = login_system.database.set_item_threshold(
            item_name,
            threshold,
        )

        if updated:
            print(f"Low-stock threshold for '{item_name}' updated.")
            display_stock_alerts(login_system)
        else:
            print("Item not found.")

    except Exception as exc:
        print(f"Unable to change stock threshold: {exc}")


def delete_inventory_item(login_system):
    """Delete an inventory record after confirmation."""
    print("\n--- Delete Inventory Item ---")

    item_name = input("Enter the exact item name: ").strip()

    if not item_name:
        print("Item name cannot be empty.")
        return

    try:
        existing = login_system.database.get_item(item_name)

        if existing is None:
            print("Item not found.")
            return

        confirmation = input(
            f"Delete '{existing['itemName']}' permanently? (y/n): "
        ).strip().lower()

        if confirmation != "y":
            print("Deletion cancelled.")
            return

        deleted = login_system.database.delete_item(item_name)

        if deleted:
            print(f"'{item_name}' was deleted.")
        else:
            print("The item could not be deleted.")

    except Exception as exc:
        print(f"Unable to delete inventory item: {exc}")


def get_nonnegative_integer(
    prompt,
    default=None,
):
    """Read a nonnegative integer from the console."""
    while True:
        value = input(prompt).strip()

        if value == "" and default is not None:
            return default

        try:
            number = int(value)

            if number < 0:
                print("Please enter zero or a positive whole number.")
                continue

            return number

        except ValueError:
            print("Invalid input. Enter a whole number.")


def inventory_menu(login_system):
    """Display the authenticated inventory menu."""
    while True:
        print("\n" + "=" * 42)
        print("       INVENTORY MANAGEMENT")
        print("=" * 42)
        print("1. View inventory")
        print("2. Add inventory item")
        print("3. Update item quantity")
        print("4. Delete inventory item")
        print("5. View stock alerts")
        print("6. Change low-stock threshold")
        print("7. Log out")
        print("8. Exit application")

        choice = input("Choose an option (1-8): ").strip()

        if choice == "1":
            display_inventory(login_system)
        elif choice == "2":
            add_inventory_item(login_system)
        elif choice == "3":
            update_inventory_item(login_system)
        elif choice == "4":
            delete_inventory_item(login_system)
        elif choice == "5":
            display_stock_alerts(login_system)
        elif choice == "6":
            change_stock_threshold(login_system)
        elif choice == "7":
            login_system.logout()
            return "logout"
        elif choice == "8":
            return "exit"
        else:
            print("Invalid selection. Choose an option from 1 to 8.")


def main():
    """Run the login, registration, and inventory workflows."""
    login_system = None

    try:
        login_system = Login()
        print("Welcome to the Inventory Management System!")

        while True:
            print("\n--- Main Menu ---")
            print("1. Log in")
            print("2. Register")
            print("3. Exit")

            choice = input("Choose an option (1-3): ").strip()

            if choice == "1":
                username = input("Username: ").strip()
                password = input("Password: ")

                if login_system.login(username, password):
                    result = inventory_menu(login_system)

                    if result == "exit":
                        break

            elif choice == "2":
                username = input("Choose a username: ").strip()
                password = input("Choose a password (minimum 8 characters): ")
                confirmation = input("Confirm password: ")

                if password != confirmation:
                    print("Passwords do not match.")
                    continue

                login_system.register(username, password)

            elif choice == "3":
                print("Exiting Inventory Management System.")
                break

            else:
                print("Invalid selection. Choose 1, 2, or 3.")

    except (KeyboardInterrupt, EOFError):
        print("\nApplication interrupted. Exiting safely.")

    except Exception as exc:
        print(f"Application could not start or continue: {exc}")

    finally:
        if login_system is not None:
            try:
                login_system.close()
            except Exception as exc:
                print(f"Warning: database cleanup failed: {exc}")

        print("Application closed.")


if __name__ == "__main__":
    main()
