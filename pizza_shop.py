import time
import os

DB_FILE = "users_database.txt"
MENU_FILE = "pizza_menu.txt"



users_db = {}
food_main = {}


def load_database():
    global users_db
    if not os.path.exists(DB_FILE):
        users_db = default_users.copy()
        save_database()
        return

    users_db = {}
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
            file.write(f"{login};{data['password']};{data['balance']}")


def load_menu():
    global food_main
    if not os.path.exists(MENU_FILE):
        food_main = default_menu.copy()
        save_menu()
        return

    food_main = {}
    with open(MENU_FILE, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            parts = line.split(";")
            if len(parts) == 2:
                item, price = parts
                food_main[item] = int(price)


def save_menu():
    with open(MENU_FILE, "w", encoding="utf-8") as file:
        for item, price in food_main.items():
            file.write(f"{item};{price}")


def save_order_to_file(login, food_item):
    filename = f"{login}_orders.txt"
    with open(filename, "a", encoding="utf-8") as file:
        file.write(f"{food_item}")


def get_orders_from_file(login):
    filename = f"{login}_orders.txt"
    if not os.path.exists(filename):
        return []
    with open(filename, "r", encoding="utf-8") as file:
        return [line.strip() for line in file.readlines() if line.strip()]


# --- ОСНОВНЫЕ ФУНКЦИИ ---

def add_user():
    print("\n--- Создание новой учетной записи ---")
    user_login = input("Введи имя пользователя: ")
    if user_login in users_db:
        print("Пользователь с таким именем уже существует!")
        return
    
    user_password = input("Введи пароль для учетной записи: ")
    users_db[user_login] = {"password": user_password, "balance": 0}
    save_database()
    print("Учетная запись успешно создана!")
    os.system("cls")


def change_user():
    print("\n--- Изменение учетной записи ---")
    input_login = input("Введи свой логин: ")
    input_password = input("Введи свой пароль: ")
    
    if input_login in users_db and users_db[input_login]["password"] == input_password:
        print("Успешный вход!")
        new_login = input("Введи новое имя пользователя: ")
        new_password = input("Введи новый пароль: ")
        
        user_data = users_db.pop(input_login)
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
    
    if input_login in users_db and users_db[input_login]["password"] == input_password:
        confirmation = input("Вы действительно хотите удалить учетку? (y/n): ").lower()
        if confirmation == "y":
            if input_login == "Admin":
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

def admin_account_menu():
    while True:
        print("")
        print("-------- МЕНЮ АДМИНИСТРАТОРА --------")
        print("0. Выход из панели управления")
        print("1. Посмотреть заказы ВСЕХ пользователей")
        print("2. Добавить / Изменить цену товара")
        print("3. Удалить товар из меню")
        print("4. Посмотреть балансы всех пользователей")
        print("")
        
        choice = input("Выбери действие администратора: ")
        
        if choice == "0":
            print("Выход из админ-панели...")
            time.sleep(1)
            os.system("cls")
            break
            
            
        elif choice == "1":
            print("\n--- ИСТОРИЯ ЗАКАЗОВ ВСЕХ КЛИЕНТОВ ---")
            for user in users_db.keys():
                orders = get_orders_from_file(user)
                order_list = ", ".join(orders) if orders else "Нет заказов"
                print(f"Пользователь [{user}]: {order_list}")
            input("\nНажмите Enter, чтобы продолжить...")
            
        elif choice == "2":
            print("\nТекущее меню пиццерии:")
            if food_main:
                for item, price in food_main.items():
                    print(f"- {item}: {price} руб.")
            else:
                print("(меню пустое)")
                
            item_name = input("\nВведите название товара (для добавления или изменения): ")
            try:
                new_price = int(input(f"Введите цену для '{item_name}': "))
                if new_price >= 0:
                    food_main[item_name] = new_price
                    save_menu()
                    print(f"Товар '{item_name}' теперь стоит {new_price} руб. и сохранен в txt файл!")
                else:
                    print("Цена не может быть отрицательной.")
            except ValueError:
                print("Ошибка! Цена должна быть числом.")
            time.sleep(1.5)
            
        elif choice == "3":
            print("\nТекущее меню пиццерии:")
            if not food_main:
                print("(меню пустое, удалять нечего)")
                time.sleep(1)
                continue
                
            for item, price in food_main.items():
                print(f"- {item}: {price} руб.")
                
            item_to_delete = input("\nВведите точное название товара для удаления: ")
            if item_to_delete in food_main:
                food_main.pop(item_to_delete)
                save_menu()
                print(f"Товар '{item_to_delete}' успешно удален из меню и txt файла!")
            else:
                print("Такого товара нет в меню.")
            time.sleep(1.5)
            
        elif choice == "4":
            print("\n--- БАЛАНСЫ ВСЕХ ПОЛЬЗОВАТЕЛЕЙ ---")
            for user, data in users_db.items():
                print(f"Пользователь [{user}]: {data['balance']} руб.")
            input("\nНажмите Enter, чтобы продолжить...")
        else:
            print("Неверный ввод! Повторите действие.")


def user_account_menu(login):
    while True:
        current_balance = users_db[login]["balance"]
        print(f"\n-------- Меню пользователя ({login}) ---------")
        print(f"Ваш текущий баланс: {current_balance} руб.")
        print("0. Выход из аккаунта")
        print("1. Посмотреть меню")
        print("2. Сделать заказ")
        print("3. Посмотреть последние заказы")
        print("4. Пополнить баланс") 
        
        choice = input("Выбери действие: ")
        
        if choice == "0":
            print("Выход из аккаунта...")
            time.sleep(1)
            os.system("cls")
            break
            
        elif choice == "1":
            print("\nДоступное меню:")
            if food_main:
                for item, price in food_main.items():
                    print(f"- {item}: {price} руб.")
            else:
                print("Извините, меню в данный момент пустое.")
            time.sleep(1.5)
            
        elif choice == "2":
            if not food_main:
                print("\nИзвините, меню пустое. Заказать ничего нельзя.")
                time.sleep(1.5)
                continue
                
            print("\nДоступное меню:")
            for item, price in food_main.items():
                print(f"- {item}: {price} руб.")
                
            choice_food = input("Выберите товар (напишите название): ")
            
            if choice_food in food_main:
                price = food_main[choice_food]
                
                if users_db[login]["balance"] >= price:
                    users_db[login]["balance"] -= price
                    save_database()
                    save_order_to_file(login, choice_food)
                    print(f"Товар '{choice_food}' успешно заказан!")
                    print(f"Ваш заказ будет готов через 20 минут")
                    print(f"Ваш остаток на балансе: {users_db[login]['balance']} руб.")
                else:
                    print(f"\n Недостаточно денег! Товар стоит {price} руб., а у вас только {users_db[login]['balance']} руб.")
                    try:
                        amount = int(input("Введите сумму для пополнения баланса: "))
                        if amount > 0:
                            users_db[login]["balance"] += amount
                            save_database()
                            print(f"Баланс успешно пополнен! Теперь у вас {users_db[login]['balance']} руб. Попробуйте сделать заказ снова.")
                        else:
                            print("Сумма пополнения должна быть больше 0.")
                    except ValueError:
                        print("Ошибка! Введено не число.")
            else:
                print("Такого товара нет в меню.")
            time.sleep(1.5)
            
        elif choice == "3":
            orders = get_orders_from_file(login)
            print(f"\nВаши заказы: {', '.join(orders) if orders else 'Нет заказов'}")
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
    
    if input_login in users_db and users_db[input_login]["password"] == input_password:
        print("Успешный вход!")
        if input_login == "Admin":
            admin_account_menu()
        else:
            user_account_menu(input_login)
    else:
        print("Неверный логин или пароль.")

def main():
    load_database()
    load_menu()
    print("Добро пожаловать в пиццерию!")
    
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
