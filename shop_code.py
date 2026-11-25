#Gfhjkm от админки admin
import time
import os
import hashlib
import secrets

DB_FILE = "users_database.txt"
MENU_FILE = "pizza_menu.txt"
ADMIN_LOGIN = "Admin"
users_db = {}
food_main = {}


def hash_password(password):
    salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 200000)
    return f"{salt}:{h.hex()}"


def verify_password(password, stored):
    if ":" not in stored:
        return False
    salt, phash = stored.split(":", 1)
    h = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 200000)
    return secrets.compare_digest(h.hex(), phash)


def load_database():
    global users_db
    users_db = {}
    if not os.path.exists(DB_FILE):
        if ADMIN_LOGIN not in users_db:
            users_db[ADMIN_LOGIN] = {"password": hash_password("admin"), "balance": 0}
        save_database()
        return
    with open(DB_FILE, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            parts = line.split(";")
            if len(parts) == 3:
                login, password, balance = parts
                users_db[login] = {"password": password, "balance": int(balance)}


def save_database():
    with open(DB_FILE, "w", encoding="utf-8") as file:
        for login, data in users_db.items():
            file.write(f"{login};{data['password']};{data['balance']}\n")


def load_menu():
    global food_main
    food_main = {}
    if not os.path.exists(MENU_FILE):
        save_menu()
        return
    with open(MENU_FILE, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            parts = line.split(";")
            if len(parts) == 3:
                item, price, qty = parts
                food_main[item] = {"price": int(price), "qty": int(qty)}


def save_menu():
    with open(MENU_FILE, "w", encoding="utf-8") as file:
        for item, data in food_main.items():
            file.write(f"{item};{data['price']};{data['qty']}\n")


def save_order_to_file(login, items_list):
    filename = f"{login}_orders.txt"
    with open(filename, "a", encoding="utf-8") as file:
        for name, qty in items_list:
            file.write(f"{name} x{qty}\n")


def get_orders_from_file(login):
    filename = f"{login}_orders.txt"
    if not os.path.exists(filename):
        return []
    with open(filename, "r", encoding="utf-8") as file:
        return [line.strip() for line in file.readlines() if line.strip()]


def get_last_orders(login, count=5):
    all_orders = get_orders_from_file(login)
    return all_orders[-count:] if len(all_orders) > count else all_orders


def check_credentials(login, password):
    if login not in users_db:
        return False
    stored = users_db[login]["password"]
    if login == ADMIN_LOGIN:
        return verify_password(password, stored)
    return stored == password


def receipt(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if result and isinstance(result, dict) and "items" in result:
            width = 46
            print()
            print("-" * width)
            print("|" + " МАГАЗИН 'ВКУСНЯШКА' ".center(width - 2) + "|")
            print("-" * width)
            for item_name, item_price, item_qty in result["items"]:
                line_text = f"{item_name} x{item_qty}"
                price_str = f"{item_price * item_qty} руб."
                dots = width - len(line_text) - len(price_str) - 4
                if dots < 1:
                    dots = 1
                print(f"| {line_text} {'.' * dots} {price_str} |")
            print("-" * width)
            total_str = f"{result['total']} руб."
            dots_total = width - len("Итого: ") - len(total_str) - 4
            if dots_total < 1:
                dots_total = 1
            print(f"| Итого: {'.' * dots_total} {total_str} |")
            bal_str = f"{result['balance']} руб."
            dots_bal = width - len("Остаток: ") - len(bal_str) - 4
            if dots_bal < 1:
                dots_bal = 1
            print(f"| Остаток: {'.' * dots_bal} {bal_str} |")
            print("-" * width)
        return result
    return wrapper


def show_users_with_orders(func):
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        load_database()
        print()
        print("=" * 50)
        print("|" + " СИСТЕМА УЧЕТА ЗАКАЗОВ ".center(48) + "|")
        print("=" * 50)
        if not users_db:
            print("|" + " Нет зарегистрированных пользователей ".center(48) + "|")
        else:
            for login, data in users_db.items():
                print("-" * 50)
                role = "АДМИН" if login == ADMIN_LOGIN else "ПОЛЬЗОВАТЕЛЬ"
                print(f"| {login} [{role}] | Баланс: {data['balance']} руб.".ljust(48) + "|")
                last_orders = get_last_orders(login, 5)
                if last_orders:
                    print("| Последние заказы:".ljust(48) + "|")
                    for idx, order in enumerate(last_orders, 1):
                        order_line = f"  {idx}. {order}"
                        print(f"| {order_line}".ljust(48) + "|")
                else:
                    print("| Последние заказы: нет".ljust(48) + "|")
        print("=" * 50)
        input("\nНажмите Enter, чтобы продолжить...")
    return wrapper


def add_user():
    print("\n--- Создание новой учетной записи ---")
    user_login = input("Введи имя пользователя: ")
    if user_login in users_db:
        print("Пользователь с таким именем уже существует!")
        return
    user_password = input("Введи пароль для учетной записи: ")
    if user_login == ADMIN_LOGIN:
        users_db[user_login] = {"password": hash_password(user_password), "balance": 0}
    else:
        users_db[user_login] = {"password": user_password, "balance": 0}
    save_database()
    print("Учетная запись успешно создана!")
    os.system("cls")


def change_user():
    print("\n--- Изменение учетной записи ---")
    input_login = input("Введи свой логин: ")
    input_password = input("Введи свой пароль: ")
    if check_credentials(input_login, input_password):
        print("Успешный вход!")
        new_login = input("Введи новое имя пользователя: ")
        new_password = input("Введи новый пароль: ")
        user_data = users_db.pop(input_login)
        if new_login == ADMIN_LOGIN:
            user_data["password"] = hash_password(new_password)
        else:
            user_data["password"] = new_password
        users_db[new_login] = user_data
        save_database()
        old_filename = f"{input_login}_orders.txt"
        new_filename = f"{new_login}_orders.txt"
        if os.path.exists(old_filename):
            os.rename(old_filename, new_filename)
        print("Данные учетки изменены!")
    else:
        print("Неверный логин или пароль.")
    os.system("cls")


def delete_user():
    print("\n!!! Перед удалением аккаунта авторизируйтесь в нем !!!")
    input_login = input("Введи свой логин: ")
    input_password = input("Введи свой пароль: ")
    if check_credentials(input_login, input_password):
        confirmation = input("Вы действительно хотите удалить учетку? (y/n): ").lower()
        if confirmation == "y":
            if input_login == ADMIN_LOGIN:
                print("!!! Учетную запись Admin удалить нельзя !!!")
            else:
                balance = users_db[input_login]["balance"]
                users_db.pop(input_login)
                save_database()
                filename = f"{input_login}_orders.txt"
                if os.path.exists(filename):
                    os.remove(filename)
                print(f"Заберите деньги со счета учетной записи: {balance} руб.")
                time.sleep(1)
                print("Учетка удалена.")
    else:
        print("Неверный логин или пароль.")
    os.system("cls")


@show_users_with_orders
def accounting_system():
    print("\nЗагрузка данных о заказах...")


def admin_account_menu():
    while True:
        load_database()
        load_menu()
        print(" ")
        print("-------- МЕНЮ АДМИНИСТРАТОРА --------")
        print("0. Выход из панели управления ")
        print("1. Посмотреть заказы ВСЕХ пользователей ")
        print("2. Добавить / Изменить цену товара ")
        print("3. Удалить товар из меню ")
        print("4. Посмотреть балансы всех пользователей ")
        print("5. Изменить количество порций товара ")
        print("6. Система учета заказов ")
        print(" ")
        choice = input("Выбери действие администратора: ")
        if choice == "0":
            print("Выход из админ-панели...")
            time.sleep(1)
            os.system("cls")
            break
        elif choice == "1":
            load_database()
            print("\n--- ИСТОРИЯ ЗАКАЗОВ ВСЕХ КЛИЕНТОВ ---")
            for user in users_db.keys():
                orders = get_orders_from_file(user)
                order_list = ", ".join(orders) if orders else "Нет заказов"
                print(f"Пользователь [{user}]: {order_list}")
            input("\nНажмите Enter, чтобы продолжить...")
        elif choice == "2":
            print("\nТекущее меню магазина:")
            if food_main:
                for item, data in food_main.items():
                    print(f"- {item}: {data['price']} руб. (остаток: {data['qty']})")
            else:
                print("(меню пустое)")
            item_name = input("\nВведите название товара (для добавления или изменения): ")
            try:
                new_price = int(input(f"Введите цену для '{item_name}': "))
                if new_price < 0:
                    print("Цена не может быть отрицательной.")
                    time.sleep(1.5)
                    continue
                if item_name in food_main:
                    food_main[item_name]["price"] = new_price
                else:
                    try:
                        new_qty = int(input(f"Введите начальное количество порций для '{item_name}': "))
                        if new_qty < 0:
                            print("Количество не может быть отрицательным.")
                            time.sleep(1.5)
                            continue
                        food_main[item_name] = {"price": new_price, "qty": new_qty}
                    except ValueError:
                        print("Ошибка! Количество должно быть числом.")
                        time.sleep(1.5)
                        continue
                save_menu()
                print(f"Товар '{item_name}' сохранен (цена: {new_price} руб.)!")
            except ValueError:
                print("Ошибка! Цена должна быть числом.")
            time.sleep(1.5)
        elif choice == "3":
            print("\nТекущее меню магазина:")
            if not food_main:
                print("(меню пустое, удалять нечего)")
                time.sleep(1)
                continue
            for item, data in food_main.items():
                print(f"- {item}: {data['price']} руб. (остаток: {data['qty']})")
            item_to_delete = input("\nВведите точное название товара для удаления: ")
            if item_to_delete in food_main:
                food_main.pop(item_to_delete)
                save_menu()
                print(f"Товар '{item_to_delete}' успешно удален из меню и txt файла!")
            else:
                print("Такого товара нет в меню.")
            time.sleep(1.5)
        elif choice == "4":
            load_database()
            print("\n--- БАЛАНСЫ ВСЕХ ПОЛЬЗОВАТЕЛЕЙ ---")
            for user, data in users_db.items():
                print(f"Пользователь [{user}]: {data['balance']} руб.")
            input("\nНажмите Enter, чтобы продолжить...")
        elif choice == "5":
            print("\n--- ИЗМЕНЕНИЕ КОЛИЧЕСТВА ПОРЦИЙ ---")
            if not food_main:
                print("(меню пустое)")
                time.sleep(1)
                continue
            for idx, (item, data) in enumerate(food_main.items(), start=1):
                print(f"{idx}. {item} - {data['price']} руб. (остаток: {data['qty']})")
            item_choice = input("\nВведите номер товара: ")
            try:
                item_idx = int(item_choice)
                items_list = list(food_main.keys())
                if 1 <= item_idx <= len(items_list):
                    chosen_item = items_list[item_idx - 1]
                    try:
                        new_qty = int(input(f"Введите новое количество порций для '{chosen_item}': "))
                        if new_qty < 0:
                            print("Количество не может быть отрицательным.")
                        else:
                            food_main[chosen_item]["qty"] = new_qty
                            save_menu()
                            print(f"Количество порций '{chosen_item}' изменено на {new_qty}!")
                    except ValueError:
                        print("Ошибка! Количество должно быть числом.")
                else:
                    print("Такого номера нет в списке.")
            except ValueError:
                print("Ошибка! Введите число.")
            time.sleep(1.5)
        elif choice == "6":
            accounting_system()
        else:
            print("Неверный ввод! Повторите действие.")


@receipt
def make_order(login):
    cart = []
    total = 0
    while True:
        load_menu()
        print("\nДоступное меню:")
        items_list = list(food_main.items())
        available = False
        for idx, (item, data) in enumerate(items_list, start=1):
            if data["qty"] > 0:
                print(f"{idx}. {item} - {data['price']} руб. (остаток: {data['qty']})")
                available = True
            else:
                print(f"{idx}. {item} - {data['price']} руб. (НЕТ В НАЛИЧИИ)")
        if not available:
            print("\nВсе товары закончились!")
            return None
        print("0. Оформить заказ")
        choice = input("\nВыберите номер товара: ")
        if choice == "0":
            if not cart:
                print("Корзина пуста! Добавьте хотя бы один товар.")
                time.sleep(1)
                continue
            break
        try:
            item_idx = int(choice)
            if not (1 <= item_idx <= len(items_list)):
                print("Такого номера нет в списке.")
                time.sleep(1)
                continue
            chosen_name = items_list[item_idx - 1][0]
            chosen_data = items_list[item_idx - 1][1]
            if chosen_data["qty"] <= 0:
                print(f"Товар '{chosen_name}' закончился! Выберите другой.")
                time.sleep(1)
                continue
            qty_input = input(f"Введите количество '{chosen_name}' (доступно: {chosen_data['qty']}): ")
            try:
                qty = int(qty_input)
                if qty <= 0:
                    print("Количество должно быть больше 0.")
                    time.sleep(1)
                    continue
                if qty > chosen_data["qty"]:
                    print(f"Недостаточно товара! Доступно только {chosen_data['qty']} порций.")
                    time.sleep(1)
                    continue
                item_total = chosen_data["price"] * qty
                cart.append((chosen_name, chosen_data["price"], qty))
                total += item_total
                print(f"Добавлено: {chosen_name} x{qty} = {item_total} руб.")
            except ValueError:
                print("Ошибка! Введите число.")
                time.sleep(1)
        except ValueError:
            print("Ошибка! Введите номер товара.")
            time.sleep(1)
    load_database()
    if users_db[login]["balance"] < total:
        print(f"\nНедостаточно денег! Заказ стоит {total} руб., а у вас {users_db[login]['balance']} руб.")
        try:
            amount = int(input("Введите сумму для пополнения баланса: "))
            if amount > 0:
                users_db[login]["balance"] += amount
                save_database()
                print(f"Баланс пополнен! Теперь у вас {users_db[login]['balance']} руб.")
            else:
                print("Сумма должна быть больше 0. Заказ отменен.")
                return None
        except ValueError:
            print("Ошибка! Введено не число. Заказ отменен.")
            return None
        if users_db[login]["balance"] < total:
            print("Всё равно недостаточно денег. Заказ отменен.")
            return None
    users_db[login]["balance"] -= total
    for name, price, qty in cart:
        food_main[name]["qty"] -= qty
    save_database()
    save_menu()
    save_order_to_file(login, [(name, qty) for name, price, qty in cart])
    return {
        "items": cart,
        "total": total,
        "balance": users_db[login]["balance"],
    }


def user_account_menu(login):
    while True:
        load_database()
        load_menu()
        current_balance = users_db[login]["balance"]
        print(f"\n-------- Меню пользователя ({login}) ---------")
        print(f"Ваш текущий баланс: {current_balance} руб. ")
        print("0. Выход из аккаунта ")
        print("1. Посмотреть меню ")
        print("2. Сделать заказ ")
        print("3. Посмотреть последние заказы ")
        print("4. Пополнить баланс ")
        choice = input("Выбери действие: ")
        if choice == "0":
            print("Выход из аккаунта...")
            time.sleep(1)
            os.system("cls")
            break
        elif choice == "1":
            print("\nДоступное меню:")
            if food_main:
                for item, data in food_main.items():
                    status = f"(остаток: {data['qty']})" if data["qty"] > 0 else "(НЕТ В НАЛИЧИИ)"
                    print(f"- {item}: {data['price']} руб. {status}")
            else:
                print("Извините, меню в данный момент пустое.")
            time.sleep(1.5)
        elif choice == "2":
            if not food_main:
                print("\nИзвините, меню пустое. Заказать ничего нельзя.")
                time.sleep(1.5)
                continue
            result = make_order(login)
            if result:
                print("Ваш заказ будет готов через 20 минут!")
            time.sleep(2)
        elif choice == "3":
            orders = get_orders_from_file(login)
            last_five = orders[-5:] if len(orders) > 5 else orders
            print(f"\nВаши последние заказы:")
            if last_five:
                for idx, order in enumerate(last_five, 1):
                    print(f"  {idx}. {order}")
            else:
                print("  Нет заказов")
            time.sleep(1.5)
        elif choice == "4":
            try:
                amount = int(input("Введите сумму для пополнения: "))
                if amount > 0:
                    users_db[login]["balance"] += amount
                    save_database()
                    print(f"Баланс успешно пополнен! Текущий баланс: {users_db[login]['balance']} руб.")
                else:
                    print("Сумма должна быть больше 0.")
            except ValueError:
                print("Ошибка! Введите число.")
            time.sleep(1.5)
        else:
            print("Error!!! Повторите ввод действия!")


def login_user():
    print("\n--- Вход в систему ---")
    input_login = input("Введи свой логин: ")
    input_password = input("Введи свой пароль: ")
    if check_credentials(input_login, input_password):
        print("Успешный вход!")
        if input_login == ADMIN_LOGIN:
            admin_account_menu()
        else:
            user_account_menu(input_login)
    else:
        print("Неверный логин или пароль.")


def main():
    load_database()
    load_menu()
    print("Добро пожаловать в магазин 'Вкусняшка'!")
    while True:
        print("\n------- Главное Меню ------- |")
        print("0. Самоуничтожение          |")
        print("1. Создать учётку           |")
        print("2. Изменить учётку          |")
        print("3. Удалить учётку           |")
        print("4. Войти в учетку           |")
        print("----------------------------|")
        make = input("Выбери действие: ")
        if make == "0":
            print("Самоуничтожение через:")
            for i in range(5, 0, -1):
                print(i)
                time.sleep(0.5)
            print("boom!!!")
            os.system("cls")
            exit("Работа программы завершена")
        elif make == "1":
            add_user()
        elif make == "2":
            change_user()
        elif make == "3":
            delete_user()
        elif make == "4":
            login_user()
        else:
            print("Повтори попытку\n")


if __name__ == "__main__":
    main()
