
import json
import os
import random

DATA_FILE = "wardrobe_data.json"

clothes = []


def load_data():
    global clothes

    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                clothes = json.load(file)
        except (json.JSONDecodeError, OSError):
            clothes = []


def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(clothes, file, ensure_ascii=False, indent=4)


def add_clothing():
    print("\n====== Add Clothing ======")

    name = input("Clothing name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return

    print("\nSelect clothing type:")
    print("1. Top")
    print("2. Bottom")
    print("3. Shoes")
    print("4. Outerwear")
    print("5. Accessories")

    types = {
        "1": "Top",
        "2": "Bottom",
        "3": "Shoes",
        "4": "Outerwear",
        "5": "Accessories"
    }

    choice = input("Enter choice: ")

    if choice not in types:
        print("Invalid choice.")
        return

    color = input("Enter clothing color: ").strip()

    clothing = {
        "name": name,
        "type": types[choice],
        "color": color
    }

    clothes.append(clothing)
    save_data()

    print("Clothing added successfully!")


def view_clothes():
    print("\n====== My Wardrobe ======")

    if not clothes:
        print("Your wardrobe is empty.")
        return

    for index, item in enumerate(clothes, 1):
        print(
            f"{index}. {item['name']} | "
            f"{item['type']} | {item['color']}"
        )


def recommend_outfit():
    print("\n====== Outfit Recommendation ======")

    tops = [item for item in clothes if item["type"] == "Top"]
    bottoms = [item for item in clothes if item["type"] == "Bottom"]
    shoes = [item for item in clothes if item["type"] == "Shoes"]

    if not tops or not bottoms or not shoes:
        print("Please add at least one top, bottom, and pair of shoes.")
        return

    top = random.choice(tops)
    bottom = random.choice(bottoms)
    shoe = random.choice(shoes)

    print("\nYour recommended outfit:")
    print(f"Top: {top['name']} ({top['color']})")
    print(f"Bottom: {bottom['name']} ({bottom['color']})")
    print(f"Shoes: {shoe['name']} ({shoe['color']})")


def save_outfit():
    print("\n====== Save Today's Outfit ======")

    if not clothes:
        print("Please add clothing first.")
        return

    view_clothes()

    choice = input("\nEnter clothing numbers separated by commas: ")

    try:
        indexes = [int(x.strip()) - 1 for x in choice.split(",")]

        if not indexes or any(i < 0 or i >= len(clothes) for i in indexes):
            print("Invalid clothing number.")
            return

        outfit = [clothes[i] for i in indexes]

        history_file = "outfit_history.json"

        if os.path.exists(history_file):
            with open(history_file, "r", encoding="utf-8") as file:
                history = json.load(file)
        else:
            history = []

        history.append(outfit)

        with open(history_file, "w", encoding="utf-8") as file:
            json.dump(history, file, ensure_ascii=False, indent=4)

        print("Outfit saved successfully!")

    except ValueError:
        print("Please enter valid numbers.")


def main():
    load_data()

    while True:
        print("\n==============================")
        print("       SMART WARDROBE")
        print("==============================")
        print("1. Add clothing")
        print("2. View wardrobe")
        print("3. Recommend outfit")
        print("4. Save today's outfit")
        print("5. Exit")

        choice = input("\nChoose an option: ")

        if choice == "1":
            add_clothing()
        elif choice == "2":
            view_clothes()
        elif choice == "3":
            recommend_outfit()
        elif choice == "4":
            save_outfit()
        elif choice == "5":
            save_data()
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
