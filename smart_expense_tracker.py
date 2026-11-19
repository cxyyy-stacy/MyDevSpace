
expenses = []

# Automatically classify expenses
def classify_expense(name):
    name = name.lower()

    categories = {
        "Food": ["starbucks", "mcdonald", "restaurant", "coffee", "food", "lunch", "dinner"],
        "Transport": ["uber", "taxi", "bus", "train", "subway", "交通"],
        "Shopping": ["amazon", "clothes", "shoes", "shopping", "购物"],
        "Entertainment": ["netflix", "movie", "game", "music", "电影"],
        "Education": ["book", "course", "school", "学费", "书"]
    }

    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in name:
                return category

    return "Other"


# Add a new expense
def add_expense():
    name = input("What did you buy? ")

    try:
        amount = float(input("How much did it cost? "))
        if amount <= 0:
            print("Amount must be greater than 0.")
            return
    except ValueError:
        print("Please enter a valid amount.")
        return

    category = classify_expense(name)

    expense = {
        "name": name,
        "amount": amount,
        "category": category
    }

    expenses.append(expense)

    print(f"Expense added! Category: {category}")


# View all expenses
def view_expenses():
    if not expenses:
        print("No expenses recorded.")
        return

    for i, expense in enumerate(expenses, 1):
        print(
            f"{i}. {expense['name']} - "
            f"${expense['amount']:.2f} "
            f"({expense['category']})"
        )


# Show expense statistics
def show_summary():
    if not expenses:
        print("No data available.")
        return

    total = sum(item["amount"] for item in expenses)

    print(f"\nTotal spending: ${total:.2f}")
    print("\nCategory statistics:")

    categories = {}

    for item in expenses:
        category = item["category"]
        categories[category] = (
            categories.get(category, 0) + item["amount"]
        )

    for category, amount in categories.items():
        print(f"{category}: ${amount:.2f}")


# Main program
while True:
    print("\n===== Smart Expense Tracker =====")
    print("1. Add Expense")
    print("2. View Expenses")
    print("3. View Summary")
    print("4. Exit")

    choice = input("Choose an option: ")

    if choice == "1":
        add_expense()
    elif choice == "2":
        view_expenses()
    elif choice == "3":
        show_summary()
    elif choice == "4":
        print("Goodbye!")
        break
    else:
        print("Invalid choice. Try again.")
