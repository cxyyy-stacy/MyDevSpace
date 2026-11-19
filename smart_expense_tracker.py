
import json
import os

DATA_FILE = "expense_data.json"

categories = {
    "1": ("Food", ["正餐", "零食", "饮料", "方便面"]),
    "2": ("Transport", ["打车", "公共交通", "汽油", "停车"]),
    "3": ("Shopping", ["美妆", "护肤", "衣服", "电子产品", "日用品"]),
    "4": ("Entertainment", ["电影", "游戏", "订阅"]),
    "5": ("Education", ["书籍", "课程", "学习用品"]),
    "6": ("Housing", ["房租", "水电", "家居"]),
    "7": ("Healthcare", ["药品", "看病", "保健"]),
    "8": ("Other", ["其他"])
}

rules = {
    "方便面": ("Food", "方便面"),
    "饮料": ("Food", "饮料"),
    "零食": ("Food", "零食"),
    "打车": ("Transport", "打车"),
    "滴滴": ("Transport", "打车"),
    "公交": ("Transport", "公共交通"),
    "地铁": ("Transport", "公共交通"),
    "汽油": ("Transport", "汽油"),
    "停车": ("Transport", "停车"),
    "化妆品": ("Shopping", "美妆"),
    "口红": ("Shopping", "美妆"),
    "粉底液": ("Shopping", "美妆"),
    "护肤": ("Shopping", "护肤"),
    "衣服": ("Shopping", "衣服"),
    "电影": ("Entertainment", "电影"),
    "游戏": ("Entertainment", "游戏"),
    "书籍": ("Education", "书籍"),
    "课程": ("Education", "课程"),
    "房租": ("Housing", "房租"),
    "水电": ("Housing", "水电"),
    "药品": ("Healthcare", "药品"),
    "看病": ("Healthcare", "看病")
}

expenses = []
custom_rules = {}


def load_data():
    global expenses, custom_rules

    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                expenses = data.get("expenses", [])
                custom_rules = data.get("custom_rules", {})
        except (json.JSONDecodeError, OSError):
            print("数据文件读取失败，将从空记录开始。")


def save_data():
    data = {
        "expenses": expenses,
        "custom_rules": custom_rules
    }

    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def classify_expense(name):
    # 优先使用用户自己设置的分类
    for keyword, result in custom_rules.items():
        if keyword in name:
            return result

    # 再使用内置关键词
    for keyword, result in rules.items():
        if keyword in name:
            return result

    return None


def choose_category():
    print("\n请选择消费大类：")

    for number, (category, subcategories) in categories.items():
        print(f"{number}. {category}")

    choice = input("请输入数字：")

    if choice not in categories:
        print("选择无效。")
        return None

    category, subcategories = categories[choice]

    print("\n请选择小类：")
    for index, subcategory in enumerate(subcategories, 1):
        print(f"{index}. {subcategory}")

    sub_choice = input("请输入数字：")

    if not sub_choice.isdigit():
        print("选择无效。")
        return None

    index = int(sub_choice) - 1

    if index < 0 or index >= len(subcategories):
        print("选择无效。")
        return None

    return category, subcategories[index]


def add_expense():
    name = input("\n请输入消费名称：").strip()

    if not name:
        print("消费名称不能为空。")
        return

    amount_text = input("请输入金额：").replace(",", "").strip()

    try:
        amount = float(amount_text)
        if amount <= 0:
            print("金额必须大于 0。")
            return
    except ValueError:
        print("金额格式不正确。")
        return

    result = classify_expense(name)

    if result:
        category, subcategory = result
        print(f"自动分类：{category} - {subcategory}")
    else:
        print("暂时无法识别，请手动选择分类。")
        result = choose_category()

        if result is None:
            print("添加失败。")
            return

        category, subcategory = result

        remember = input("是否记住这个分类？(y/n)：").lower()

        if remember == "y":
            custom_rules[name] = result

    expense = {
        "name": name,
        "amount": amount,
        "category": category,
        "subcategory": subcategory
    }

    expenses.append(expense)
    save_data()

    print("消费记录添加成功！")


def view_expenses():
    if not expenses:
        print("\n目前没有消费记录。")
        return

    print("\n====== 消费记录 ======")

    for item in expenses:
        print(
            f"{item['name']} | "
            f"{item['amount']:.2f} | "
            f"{item['category']} - {item['subcategory']}"
        )


def show_summary():
    if not expenses:
        print("\n目前没有消费记录。")
        return

    total = sum(item["amount"] for item in expenses)
    summary = {}

    for item in expenses:
        category = item["category"]
        subcategory = item["subcategory"]

        if category not in summary:
            summary[category] = {}

        summary[category][subcategory] = (
            summary[category].get(subcategory, 0)
            + item["amount"]
        )

    print("\n====== 消费统计 ======")
    print(f"总消费：{total:.2f}")

    for category, subcategories in summary.items():
        print(f"\n{category}")

        for subcategory, amount in subcategories.items():
            print(f"  {subcategory}: {amount:.2f}")


def main():
    load_data()

    while True:
        print("\n====== Smart Expense Tracker ======")
        print("1. 添加消费")
        print("2. 查看记录")
        print("3. 消费统计")
        print("4. 退出")

        choice = input("请选择功能：")

        if choice == "1":
            add_expense()
        elif choice == "2":
            view_expenses()
        elif choice == "3":
            show_summary()
        elif choice == "4":
            save_data()
            print("数据已保存，再见！")
            break
        else:
            print("无效选择，请重新输入。")


if __name__ == "__main__":
    main()
