import os
import time
import msvcrt
import sqlite3
import webbrowser
import csv
from datetime import datetime
import ctypes
import msvcrt
import subprocess
import sys
from ctypes import wintypes

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
user32 = ctypes.WinDLL('user32', use_last_error=True)

SW_MAXIMIZE = 3

kernel32.GetConsoleWindow.restype = wintypes.HWND
kernel32.GetLargestConsoleWindowSize.restype = wintypes._COORD
kernel32.GetLargestConsoleWindowSize.argtypes = (wintypes.HANDLE,)
user32.ShowWindow.argtypes = (wintypes.HWND, ctypes.c_int)

def maximize_console(lines=None):
    fd = os.open('CONOUT$', os.O_RDWR)
    try:
        hCon = msvcrt.get_osfhandle(fd)
        max_size = kernel32.GetLargestConsoleWindowSize(hCon)
        if max_size.X == 0 and max_size.Y == 0:
            raise ctypes.WinError(ctypes.get_last_error())
    finally:
        os.close(fd)
    cols = max_size.X
    hWnd = kernel32.GetConsoleWindow()
    if cols and hWnd:
        if lines is None:
            lines = max_size.Y
        else:
            lines = max(min(lines, 9999), max_size.Y)
        subprocess.check_call('mode.com con cols={} lines={}'.format(
                                cols, lines))
        user32.ShowWindow(hWnd, SW_MAXIMIZE)


def addEanToProduct():
    while True:
        AETP_pcode = input("Input product code (or press Enter to exit): ")
        if AETP_pcode == "":
            menu()
            break
        
        AETP_ean = input("Add EAN: ")
        
        try:
            cursor.execute("UPDATE products SET ean=? WHERE product_code=?", (AETP_ean, AETP_pcode))
            conn.commit()
            
            cursor.execute("SELECT product_name, ean FROM products WHERE product_code=?", (AETP_pcode,))
            check = cursor.fetchone() 
            
            if check:
                print(f"'{check[0]}' updated EAN to: {check[1]}")
            else:
                print("Product not found.")
        
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(0.5)

def addPriceToProduct():
    flag = ""
    while True:
        cursor.execute("SELECT product_name FROM products WHERE unit_price=?", (flag,))
        result = cursor.fetchall()
        print("Missing prices:")
        for result in result:
            print(result[result])
        AETP_pcode = input("Input product code (or press Enter to exit): ")
        if AETP_pcode == "":
            menu()
            break
        
        AETP_ean = input("Add price: ")
        
        try:
            cursor.execute("UPDATE products SET ean=? WHERE product_code=?", (AETP_ean, AETP_pcode))
            conn.commit()
            
            cursor.execute("SELECT product_name, ean FROM products WHERE product_code=?", (AETP_pcode,))
            check = cursor.fetchone() 
            
            if check:
                print(f"'{check[0]}' updated EAN to: {check[1]}")
            else:
                print("Product not found.")
        
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(0.5)


def backup_products_to_csv():
    # Set database name
    db_name = 'current_inventory.db'
    
    # Get current directory
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file_name = f"export_{timestamp}.csv"

    db_path = os.path.join(current_directory, db_name)
    csv_file_path = os.path.join(current_directory, csv_file_name)

    # get products
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()

    # column names
    column_names = [description[0] for description in cursor.description]

    # CSV file
    with open(csv_file_path, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(column_names)  # Write the header
        writer.writerows(rows)  # Write all rows

    print(f"Backup completed: {csv_file_path}")
    time.sleep(1)

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

from datetime import datetime

db_file = r"C:\Users\Kristian Lien\OneDrive - Osloskolen\LVS\Stockfox - LVS\current_inventory.db"

def console_clear():
    os.system('cls' if os.name == 'nt' else 'clear')

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

def db_init():
    # Create table if not exists
    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        product_name TEXT NOT NULL,
                        product_code TEXT NOT NULL,
                        ean INTEGER,
                        current_stock INTEGER,
                        location TEXT,
                        supplier TEXT,
                        status TEXT,
                        unit_price TEXT,
                        sale_price TEXT

                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS LVS01 (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        product_name TEXT NOT NULL,
                        product_code TEXT NOT NULL,
                        ean INTEGER,
                        current_stock INTEGER,
                        location TEXT,
                        supplier TEXT,
                        status TEXT,
                        unit_price TEXT,
                        sale_price TEXT

                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS LVS02 (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        product_name TEXT NOT NULL,
                        product_code TEXT NOT NULL,
                        ean INTEGER,
                        current_stock INTEGER,
                        location TEXT,
                        supplier TEXT,
                        status TEXT,
                        unit_price TEXT,
                        sale_price TEXT

                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        product_amount TEXT,
                        net_income TEXT,
                        profit TEXT

                    )''')   
    cursor.execute('''CREATE TABLE IF NOT EXISTS shopping_list(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_name TEXT NOT NULL,
                    product_code TEXT NOT NULL,
                    ean INTEGER,
                    current_stock INTEGER,
                    location TEXT,
                    supplier TEXT,
                    status TEXT,
                    unit_price TEXT,
                    sale_price TEXT

                    )''')
     
    conn.commit()

def get_keypress():
    return msvcrt.getch().decode('utf-8')

def pressAnyKeyForMenu():
    print("Press any key to go back to the menu...")
    get_keypress()
    menu()

db_init()

def writeToDB(product_name, product_code, ean, current_stock, location, supplier, status, unit_price, sale_price):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Insert new product the database
    cursor.execute("INSERT INTO products (product_name, product_code, ean, current_stock, location, supplier, status, unit_price, sale_price) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                   (product_name, product_code.strip(), ean.strip(), current_stock, location, supplier, status, unit_price, sale_price))
    conn.commit()

def menu():
    console_clear()
    print("   _____  _                 _     ______          ")
    print("  / ____|| |               | |   |  ____|         ")
    print(" | (___  | |_   ___    ___ | | __| |__  ___ __  __")
    print("  \___ \ | __| / _ \  / __|| |/ /|  __|/ _ \\\\ \/ /    |\/|")
    print("  ____) || |_ | (_) || (__ |   < | |  | (_) |>  <  .__.. \\")
    print(" |_____/  \__| \___/  \___||_|\_\|_|   \___//_/\_\  \____/")
    print("")
    print("1. View current stock")
    print("2. Generate picklist")
    print("3. Update product stock")
    print("4. Machine side-storage")
    print("5. Insert new product into system")
    print("6: Edit products")
    print("7: View product details")
    print("8: Remove product from system")
    print("9: Settings/information")
    print("")
    print("0: Quit StockFox")
    choice = get_keypress()
    run(choice)

def updateStockMenu():
    console_clear()
    print("Update stock:")
    print("")
    print("1. Edit stock")
    print("2. Add stock")
    print("")
    print("0. Exit")
    choice = get_keypress()
    if choice == "1":
        updateStock()
    elif choice == "2":
        addStock()
    elif choice == "0":
        menu()
    else:
        print("Invalid choice")
        time.sleep(0.5)
        updateStockMenu()

def picklist_menu():
    console_clear()
    print("Generate picklist:")
    print("")
    print("1. Picklist")
    print("2. View/edit shopping list")
    print("")
    print("0. Exit")
    choice = get_keypress()
    if choice == "1":
        generatePicklist()
    elif choice == "2":
        shopping_list()
    elif choice == "0":
        menu()
    else:
        print("Invalid choice")
        time.sleep(0.5)
        picklist_menu()

def run(choice):
    if choice == "1":
        viewStock()
    elif choice == "2":
        picklist_menu()
    elif choice == "3":
        updateStockMenu()
    elif choice == "4":
        machineSideStorage()
    elif choice == "5":
        newProduct()
    elif choice == "6":
        editProduct()
    elif choice == "7":
        console_clear()
        viewProductDetails()
    elif choice == "8":
        removeProduct()
    elif choice == "9":
        settings()
    elif choice == "0":
        print("Are you sure you want to quit? (Y/N): ")
        exit_confirm = get_keypress()
        if exit_confirm.lower() == "y":
            conn.commit()
            while True:
                sys.exit()
        else:
            menu()
    elif choice.lower() == "f":
        maximize_console()
        menu()
    
    else:
        print("Invalid choice")
        time.sleep(0.5)
        menu()


def viewStock():
    console_clear()

    # Fetch data from all tables
    cursor.execute("SELECT product_name, product_code, current_stock, location, status, unit_price FROM products")
    results = cursor.fetchall()

    cursor.execute("SELECT product_code, current_stock FROM lvs01")
    results_LVS01 = cursor.fetchall()

    cursor.execute("SELECT product_code, current_stock FROM lvs02")
    results_LVS02 = cursor.fetchall()

    # Create dictionaries for quick lookup
    lvs01_dict = {row[0]: int(row[1]) if isinstance(row[1], (int, float)) else 0 for row in results_LVS01}
    lvs02_dict = {row[0]: int(row[1]) if isinstance(row[1], (int, float)) else 0 for row in results_LVS02}

    # Sort main results by status (active first), then location, then stock (lowest first)
    results.sort(key=lambda row: (
        row[4].lower() != "active" if isinstance(row[4], str) else True,
        row[3].lower() if isinstance(row[3], str) else "",
        int(row[2]) if isinstance(row[2], (int, float)) else 0
    ))

    conn.commit()

    # Header
    print(f"{'Product Name':<30} {'Product Code':<15} {'Current Stock':<15} {'Location':<15} {'Status':<15} {'Stock Value':>10} {'LVS01 Stock':<15} {'LVS02 Stock':<15}")
    print("-" * 150)

    total_stock_value = 0

    # Print results
    for row in results:
        product_name = row[0] if isinstance(row[0], str) else "Unknown"
        product_code = row[1] if isinstance(row[1], str) else "N/A"
        current_stock = int(row[2]) if isinstance(row[2], (int, float)) else 0
        location = row[3] if isinstance(row[3], str) else "Unknown"
        status = row[4] if isinstance(row[4], str) else "N/A"
        unit_price = float(row[5]) if isinstance(row[5], (int, float)) else 0.0

        # Fetch side storage values
        lvs01_stock = lvs01_dict.get(product_code, 0)
        lvs02_stock = lvs02_dict.get(product_code, 0)

        # Check for low stock
        low_stock_warning = " (low stock!)" if current_stock < 10 and status.lower() == "active" else ""
        current_stock_display = f"{current_stock}{low_stock_warning}"

        # Status color display
        if status.lower() == "active":
            status_display = bcolors.OKGREEN + "██ ACTIVE" + bcolors.ENDC
        elif status.lower() == "inactive":
            status_display = bcolors.FAIL + "██ INACTIVE" + bcolors.ENDC
        else:
            status_display = status

        # Calculate stock value and add to total
        current_stock_value = current_stock + lvs01_stock + lvs02_stock
        stock_value = round(current_stock_value * unit_price, 2)
        total_stock_value = round(total_stock_value + stock_value, 2)

        # Print row with side storage values
        print(f"{product_name:<30} {product_code:<15} {current_stock_display:<15} {location:<15} {status_display:<24} {stock_value:<15} {lvs01_stock:<15} {lvs02_stock:<15}")

    print("")
    print(f"Total stock value: {total_stock_value}")
    print(" ")
    pressAnyKeyForMenu()



def supplyList():
    console_clear()
    print("Supply list:")
    print("")
    cursor.execute("SELECT product_name, product_code, supplier, current_stock FROM products WHERE current_stock < 15 AND status='Active'")
    
    recommended_fill = cursor.fetchall()
    
    if recommended_fill:
        print("Recommended products to fill:")
        print(f"{'Product Name':<30} {'Product Code':<15} {'Current Stock':<15} {'Supplier':<15}")
        print("-" * 80)
        for row in recommended_fill:
            product_name, product_code, supplier, current_stock = row
            print(f"{product_name:<30} {product_code:<15} {current_stock:<15} {supplier:<15}")

    else:
        print("No products need refilling.")
    
    print("")

    product_quantities = {}

    while True:
        code = input("Enter product code or EAN (press Enter to exit, type 'generate' to finish, or type 'custom' to add a custom product): ").strip()

        if code.lower() == "generate":
            break

        if code.lower() == "exit":
            if not product_quantities:
                menu()
            else:
                confirmation = input("You have unsaved products. Are you sure you want to exit? (Y/N): ").strip().lower()
                if confirmation == "y":
                    menu()
                    return

        if code == "":
            if not product_quantities:
                menu()
            else:
                confirmation = input("You have unsaved products. Are you sure you want to exit? (Y/N): ").strip().lower()
                if confirmation == "y":
                    menu()
                    return

        if code.lower() == 'custom':
            # Allow user to input custom product details
            custom_name = input("Enter custom product name: ")
            supplier = input("Enter supplier for custom product: ")
            location = input("Enter storage location for custom product: ")
            current_stock = input(f"Enter current stock for {custom_name}: ")
            fill_quantity = input(f"Enter quantity to add for {custom_name}: ")

            # Store the custom product details
            product_quantities[custom_name] = {
                "current_stock": current_stock,
                "fill_quantity": fill_quantity,
                "supplier": supplier,
                "location": location
            }
        else:
            # Fetch product details from the database, including current stock
            cursor.execute("SELECT product_name, supplier, current_stock FROM products WHERE product_code=? OR ean=?", (code.upper(), code))
            result = cursor.fetchone()

            if result:
                product_name, supplier, current_stock = result
                print(f"{product_name} has {current_stock} units in stock.")

                # Ask user how much they want to fill
                fill_quantity = input(f"Enter quantity to add for {product_name}: ")

                # Store the product details
                product_quantities[product_name] = {
                    "current_stock": current_stock,
                    "fill_quantity": fill_quantity,
                    "supplier": supplier
                }
            else:
                print("Invalid product code or EAN. Please try again.")

    # Generate HTML filling list
    current_date = datetime.now().strftime("%d-%m-%Y")
    products_with_locations = []

    for product_name, stock_data in product_quantities.items():
        if "location" in stock_data:
            location = stock_data["location"]  # For custom products
        else:
            cursor.execute("SELECT product_code, location FROM products WHERE product_name=?", (product_name,))
            result = cursor.fetchone()
            if result:
                product_code, location = result
            else:
                location = "Unknown"

        fill_quantity = stock_data["fill_quantity"]
        supplier = stock_data["supplier"]
        products_with_locations.append((product_name, supplier, fill_quantity, location))

    # Sort products
    products_with_locations.sort(key=lambda item: item[3])

    # Create HTML
    html_content = f'''
    <html>
    <head>
        <title>Filling List</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 10px; border: 1px solid black; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <img src="https://files.catbox.moe/x46dlm.png" alt="Company Logo" style="width:1250;"> <! --  REPLACE catbox.moe LINK WITH IMAGE LINK-->
        <p>Date: {current_date}</p>
        <table>
            <tr>
                <th>Product Name</th>
                <th>Supplier</th>
                <th>Quantity to Add</th>
                <th>Location</th>
            </tr>
    '''

    for product_name, supplier, fill_quantity, location in products_with_locations:
        html_content += f'''
            <tr>
                <td>{product_name}</td>
                <td>{supplier}</td>
                <td>{fill_quantity}</td>
                <td>{location}</td>
            </tr>
        '''

    html_content += '''
        </table>
    </body>
    </html>
    '''

    # Save and open HTML file
    html_file = "fillinglist.html"
    with open(html_file, "w") as file:
        file.write(html_content)

    print("HTML file created successfully. Opening it in your web browser...")

    absolute_path = os.path.abspath(html_file)
    webbrowser.open(f"file://{absolute_path}")

    pressAnyKeyForMenu()



def generatePicklist():
    console_clear()

    print("Picklist Options:")
    print("1. Fill LVS01")
    print("2. Fill LVS02")
    print("3. Storage List (no machine being filled)")
    print("4. Supply list")
    print("")

    # Prompt user to choose machine
    machine_choice = get_keypress()

    if machine_choice == "1":
        storage_table = 'LVS01'
    elif machine_choice == "2":
        storage_table = 'LVS02'
    elif machine_choice == "3":
        storage_table = None  # No machine being filled, general storage list
    elif machine_choice == "4":
        supplyList()
    else:
        print("Invalid choice")
        time.sleep(0.5)
        generatePicklist()
        

    console_clear()
    
    product_quantities = {}

    while True:
        code = input("Enter product code or EAN (press Enter to exit, type 'generate' to generate, type 'custom' to add custom product): ").strip()
        
        if code.lower() == "generate":
            break

        if code.lower() == "exit":
            if not product_quantities:
                menu()
            else:
                confirmation = input("You have unsaved products. Are you sure you want to exit? (Y/N): ").strip().lower()
                if confirmation == "y":
                    menu()
                    return

        if code == "":
            if not product_quantities:
                menu()
            else:
                confirmation = input("You have unsaved products. Are you sure you want to exit? (Y/N): ").strip().lower()
                if confirmation == "y":
                    menu()
                    return

        if code.lower() == 'custom':
            custom_name = input("Enter custom product name: ")
            quantity = input(f"Enter quantity for {custom_name}: ")
            product_quantities[custom_name] = {"from_side": 0, "from_main": quantity}
        else:
            cursor.execute("SELECT product_name, current_stock FROM products WHERE product_code=? OR ean=?", (code.upper(), code))
            result = cursor.fetchone()

            if result:
                product_name, main_stock = result
                if storage_table == "LVS01":
                    cursor.execute("SELECT current_stock FROM lvs01 WHERE product_code=?", (code.upper(),))
                    stock_in_sidestorage = cursor.fetchone()
                    stock_in_sidestorage = stock_in_sidestorage[0] if stock_in_sidestorage else None
                elif storage_table == "LVS02":
                    cursor.execute("SELECT current_stock FROM lvs02 WHERE product_code=?", (code.upper(),))
                    stock_in_sidestorage = cursor.fetchone()
                    stock_in_sidestorage = stock_in_sidestorage[0] if stock_in_sidestorage else None
                
                quantity = float(input(f"Enter quantity for {product_name} (Main storage stock: {main_stock}, Side storage stock: {stock_in_sidestorage}): "))

                if storage_table:
                    # Check side storage first if a machine is being filled
                    cursor.execute(f"SELECT current_stock FROM {storage_table} WHERE product_code=?", (code.upper(),))
                    side_stock = cursor.fetchone()
                    side_stock = side_stock[0] if side_stock else 0

                    # Priority: Fulfill from side storage first
                    if side_stock > 0:
                        if side_stock >= quantity:
                            # Fully fulfill from side storage
                            product_quantities[product_name] = {"from_side": quantity, "from_main": 0}
                        else:
                            # Partially fulfill from side storage, remainder from main storage
                            remainder = quantity - side_stock
                            product_quantities[product_name] = {"from_side": side_stock, "from_main": remainder}

                    else:
                        # If side storage is empty, fulfill from main storage
                        if quantity <= main_stock:
                            product_quantities[product_name] = {"from_side": 0, "from_main": quantity}
                        else:
                            print(f"Not enough stock available. Available in main storage: {main_stock}")
                            continue
                else:
                    # Only check main storage if not filling a machine
                    if quantity <= main_stock:
                        product_quantities[product_name] = {"from_side": 0, "from_main": quantity}
                    else:
                        print(f"Not enough stock available in main storage. Available: {main_stock}")
                        continue
            else:
                print("Invalid product code or EAN. Please try again.")

    # Generate HTML picklist
    current_date = datetime.now().strftime("%d-%m-%Y")
    products_with_locations = []

    for product_name, stock_data in product_quantities.items():
        cursor.execute("SELECT product_code, location FROM products WHERE product_name=?", (product_name,))
        result = cursor.fetchone()
        if result:
            product_code, location = result
            total_quantity = stock_data["from_side"] + stock_data["from_main"]
            products_with_locations.append((product_name, total_quantity, location, stock_data))

    # Sort products by location
    products_with_locations.sort(key=lambda item: item[2])

    # Create HTML content
    html_content = f'''
    <html>
    <head>
        <title>Lagerliste LVS</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 10px; border: 1px solid black; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>

        <! -- CHANGE LINK TO TOP IMAGE FOR PICKLIST HERE-->
        <img src="https://files.catbox.moe/x46dlm.png" alt="Company Logo" style="width:1250;"> <! --  REPLACE catbox.moe LINK WITH IMAGE LINK-->
        <! -- CHANGE LINK TO TOP IMAGE FOR PICKLIST HERE-->

        <p>Dato: {current_date}</p>
        <table>
            <tr>
                <th>Produktnavn</th>
                <th>Kvante</th>
                <th>Plassering</th>
            </tr>
    '''

    for product_name, total_quantity, location, stock_data in products_with_locations:
        side_quantity = stock_data["from_side"]
        main_quantity = stock_data["from_main"]

        quantity_info = []
        if side_quantity > 0:
            quantity_info.append(f"{side_quantity} side storage")
        if main_quantity > 0:
            quantity_info.append(f"{main_quantity} main storage")

        quantity_display = " + ".join(quantity_info)  # e.g., "10 side storage + 5 main storage"

        html_content += f'''
            <tr>
                <td>{product_name}</td>
                <td>{quantity_display}</td>
                <td>{location}</td>
            </tr>
        '''

    html_content += '''
        </table>
    </body>
    </html>
    '''

    # Save and open the HTML file
    html_file = "lagerliste.html"
    with open(html_file, "w") as file:
        file.write(html_content)

    print("HTML file created successfully. Opening it in your web browser...")

    absolute_path = os.path.abspath(html_file)
    webbrowser.open(f"file://{absolute_path}")

    # Update the stock after confirmation
    removeFromDB_choice = input("Do you want to update the inventory stock for the products in the picklist? (Y/N): ")

    if removeFromDB_choice.lower() == "y":
        for product_name, stock_data in product_quantities.items():
            # Deduct from side storage if applicable
            if stock_data["from_side"] > 0 and storage_table:
                cursor.execute(f"SELECT current_stock FROM {storage_table} WHERE product_name=?", (product_name,))
                current_side_stock = cursor.fetchone()[0]
                new_side_stock = current_side_stock - stock_data["from_side"]
                cursor.execute(f"UPDATE {storage_table} SET current_stock=? WHERE product_name=?", (new_side_stock, product_name))

            # Deduct from main storage
            if stock_data["from_main"] > 0:
                cursor.execute("SELECT current_stock FROM products WHERE product_name=?", (product_name,))
                current_main_stock = cursor.fetchone()[0]
                new_main_stock = current_main_stock - stock_data["from_main"]
                cursor.execute("UPDATE products SET current_stock=? WHERE product_name=?", (new_main_stock, product_name))

        conn.commit()
        print("Inventory updated successfully.")
        pressAnyKeyForMenu()
    else:
        print("Inventory not updated.")
        pressAnyKeyForMenu()

def shopping_list():
    console_clear()
    print("Shopping list:")
    print("")
    print("1. Add to shopping list")
    print("2. View shopping list")
    print("3. Edit shopping list")
    print("")
    print("0. Back")
    choice = get_keypress()
    if choice == "1":
        shopping_list_ADD()
    elif choice == "2":
        shopping_list_VIEW()
    elif choice == "3":
        shopping_list_EDIT()
    elif choice == "0":
        picklist_menu()
    else:
        print("Invalid choice")
        time.sleep(0.5)
        shopping_list()

def shopping_list_ADD():
    console_clear()
    print("Adding to shopping list:\n")

    while True:
        sla_pcode = input("Please enter product code or scan EAN (or press Enter to exit): ").strip().upper()
        if sla_pcode == "":
            shopping_list_VIEW()
            break
        
        # Determine if the input is an EAN (digits) or a product code (letters)
        if sla_pcode.isdigit():
            query = "SELECT * FROM products WHERE ean=?"
        elif sla_pcode.isalpha():
            query = "SELECT * FROM products WHERE product_code=?"
        else:
            print("Invalid input. Please enter a valid product code or EAN.")
            continue  # Skip to the next iteration

        cursor.execute(query, (sla_pcode,))
        product_info = cursor.fetchone()
        
        if product_info:
            # Unpack product information
            product_name, product_code, ean, current_stock, location, supplier, status, unit_price, sale_price = product_info[1:]

            cursor.execute("SELECT current_stock FROM products WHERE ean=?", (sla_pcode,))
            current_quantity = cursor.fetchone()
            current_quantity = int(current_quantity[0]) if current_quantity else 0  # Extract the value or default to 0

            # Fetch the current stock from 'lvs01' 
            cursor.execute("SELECT current_stock FROM lvs01 WHERE ean=?", (sla_pcode,))
            current_quantity_lvs01 = cursor.fetchone()
            current_quantity_lvs01 = int(current_quantity_lvs01[0]) if current_quantity_lvs01 else 0  # Extract the value or default to 0

            # Fetch the current stock from 'lvs02' 
            cursor.execute("SELECT current_stock FROM lvs02 WHERE ean=?", (sla_pcode,))
            current_quantity_lvs02 = cursor.fetchone()
            current_quantity_lvs02 = int(current_quantity_lvs02[0]) if current_quantity_lvs02 else 0  # Extract the value or default to 0

            #total quantity
            total_quantity = current_quantity + current_quantity_lvs01 + current_quantity_lvs02

            cursor.execute("SELECT current_stock FROM shopping_list WHERE ean=? or product_code=?", (sla_pcode, sla_pcode,))
            current_quantity_shopping_list = cursor.fetchone()

            # Print the product info and current stock
            print(f"{product_name} has {total_quantity} in storage (Main storage: {current_quantity}, LVS01: {current_quantity_lvs01}, LVS02: {current_quantity_lvs02}, Shopping list: {current_quantity_shopping_list[0]})")

            # shopping list
            sla_product_qty = input(f"Please enter the quantity of {product_name} you want to add to the shopping list: ").strip()
            
            if not sla_product_qty.isdigit() or int(sla_product_qty) <= 0:
                print("Please enter a valid positive quantity.")
                continue
            
            sla_product_qty = int(sla_product_qty)

            # Check if product already exists
            cursor.execute("SELECT current_stock FROM shopping_list WHERE product_name=? AND product_code=?", (product_name, product_code))
            existing_result = cursor.fetchone()

            if existing_result:
                # Update the quantity if product already exists
                new_quantity = existing_result[0] + sla_product_qty
                cursor.execute("UPDATE shopping_list SET current_stock=? WHERE product_name=? AND product_code=?", (new_quantity, product_name, product_code))
            else:
                # Insert new product into the shopping list
                cursor.execute('''INSERT INTO shopping_list (product_name, product_code, ean, current_stock, location, supplier, status, unit_price, sale_price) 
                                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                                  (product_name, product_code, ean, sla_product_qty, location, supplier, status, unit_price, sale_price))

            conn.commit()
            print(f"{sla_product_qty} of {product_name} has been added to the shopping list.")

            # Update total quantity for items in the shopping list
            cursor.execute("SELECT SUM(current_stock) FROM shopping_list WHERE product_name=? AND product_code=?", (product_name, product_code))
            shopping_list_quantity = cursor.fetchone()
            total_in_shopping_list = shopping_list_quantity[0] if shopping_list_quantity and shopping_list_quantity[0] else 0
            print(f"Total {product_name} in shopping list: {total_in_shopping_list}")

        else:
            print("Product not found. Would you like to add a custom product? (Y/N)")
            if input().strip().lower() == 'y':
                # Prompt for the custom product name only
                product_name = sla_pcode.strip()

                # Default values
                product_code = "CUSTOM"
                ean = None
                current_stock = input(f"Please input quantity for {sla_pcode}: ")
                location = "Unspecified"
                supplier = "Unknown"
                status = "Active"
                unit_price = 0.0
                sale_price = 0.0

                # Insert custom product into the products table

                cursor.execute('''INSERT INTO shopping_list (product_name, product_code, ean, current_stock, location, supplier, status, unit_price, sale_price) 
                                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                                  (product_name, product_code, ean, current_stock, location, supplier, status, unit_price, sale_price))  # Default quantity for custom product

                conn.commit()
                print(f"Custom product {product_name} has been added to the shopping list.")

            else:
                print("Please check the code or EAN and try again.")


def shopping_list_VIEW():
    console_clear()
    print("Shopping List:")
    print("")
    
    # Fetch all items from the shopping list
    cursor.execute("SELECT product_name, product_code, current_stock FROM shopping_list")
    items = cursor.fetchall()
    
    if items:
        print(f"{'Product Name':<30} {'Product Code':<15} {'Quantity':<10}")
        print("-" * 60)
        for item in items:
            product_name, product_code, current_stock = item
            print(f"{product_name:<30} {product_code:<15} {current_stock:<10}")
    else:
        print("Your shopping list is empty.")
    
    print("")
    print("Press any key to go back")
    get_keypress()
    shopping_list()


def shopping_list_EDIT():
    console_clear()
    print("Edit Shopping List: Remove Item\n")

    # Fetch all items from the shopping list
    cursor.execute("SELECT product_name, product_code FROM shopping_list")
    items = cursor.fetchall()

    if items:
        print(f"{'Product Name':<30} {'Product Code':<15}")
        print("-" * 45)
        for index, item in enumerate(items):
            product_name, product_code = item
            print(f"{index + 1}. {product_name:<30} {product_code:<15}")

        try:
            remove_choice = int(input("\nEnter the number of the item you want to remove (or 0 to cancel): "))
            if remove_choice == 0:
                return 

            if 1 <= remove_choice <= len(items):
                selected_item = items[remove_choice - 1]
                product_name, product_code = selected_item

                # Remove the selected item from the shopping list
                cursor.execute("DELETE FROM shopping_list WHERE product_name=? AND product_code=?", (product_name, product_code))
                conn.commit()
                print(f"{product_name} has been removed from the shopping list.")
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
    else:
        print("Your shopping list is empty.")

    shopping_list()  # Wait for user input before returning to the menu


def updateStock():
    console_clear()
    print("Update stock:")
    print("")
    while True:
        us_pcode = input("Enter product code or EAN (orn press Enter to save/exit): ")
        if us_pcode == "":
            menu()
        elif us_pcode.isdigit():
            cursor.execute("SELECT product_name FROM products WHERE ean=?", (us_pcode,))
            result = cursor.fetchone() 
            if result:
                cursor.execute("SELECT current_stock FROM products WHERE ean=?", (us_pcode,))
                current_quantity = cursor.fetchone() 
                product_name = result[0]
                us_quantity = input(f"Enter quantity of {product_name} (current quantity: {current_quantity[0]}): ")
                cursor.execute("UPDATE products SET current_stock = ? WHERE ean=?", 
                               (us_quantity, us_pcode))
                cursor.execute("SELECT current_stock FROM products WHERE ean=?", (us_pcode,))
                conn.commit()
                updatedQuantity = cursor.fetchone()
                if updatedQuantity:
                    print(f"{product_name} quantity is now: {updatedQuantity[0]}")
                else:
                    print(bcolors.WARNING + "WARNING: There seems to be an issue with the DB. Please double check quantity." + bcolors.ENDC)
            else:
                print("Product not found.")
                time.sleep(0.5)
                updateStock()

        else:
            cursor.execute("SELECT product_name FROM products WHERE product_code=?", (us_pcode,))
            result = cursor.fetchone() 
            if result:
                cursor.execute("SELECT current_stock FROM products WHERE product_code=?", (us_pcode,))
                current_quantity = cursor.fetchone() 
                product_name = result[0]
                us_quantity = input(f"Enter quantity of {product_name} (current quantity: {current_quantity[0]}): ")
                cursor.execute("UPDATE products SET current_stock = ? WHERE product_code=?", 
                (us_quantity, us_pcode))
                cursor.execute("SELECT current_stock FROM products WHERE product_code=?", (us_pcode,))
                updatedQuantity = cursor.fetchone()
                if updatedQuantity:
                    print(f"{product_name} quantity is now: {updatedQuantity[0]}")
                else:
                    print(bcolors.WARNING + "WARNING: There seems to be an issue with the DB. Please double check quantity." + bcolors.ENDC)

            else:
                print("Product not found.")
                time.sleep(0.5)
                updateStock()


def addStock():
    console_clear()
    print("Add stock:")
    print("")
    while True: 
        as_pcode = input("Enter product code or scan barcode (or press Enter to save/exit): ")
        if as_pcode == "":
            menu()
        elif as_pcode.isdigit():
            cursor.execute("SELECT product_name FROM products WHERE ean=?", (as_pcode,))
            result = cursor.fetchone() 
            if result:
                product_name = result[0]
                as_quantity = input(f"Enter quantity of {product_name} to be added to inventory: ")
                cursor.execute("UPDATE products SET current_stock = current_stock + ? WHERE ean=?", 
                               (as_quantity, as_pcode))
            else:
                print("Product not found.")
                time.sleep(0.5)
                addStock()
        else:
            cursor.execute("SELECT product_name FROM products WHERE product_code=?", (as_pcode,))
            result = cursor.fetchone()
            if result:
                product_name = result[0]
                as_quantity = input(f"Enter quantity of {product_name} to be added to inventory: ")
                cursor.execute("UPDATE products SET current_stock = current_stock + ? WHERE product_code=?", 
                               (as_quantity, as_pcode))
                conn.commit()
            else:
                print("Product not found.")
                time.sleep(0.5)
                addStock()

def machineSideStorage():
    console_clear()
    print("Machine side storage (press any key to exit):")
    print("")
    print("1. LVS01")
    print("2. LVS02")
    print("3. View all side storage stocks")
    print("")
    choice = get_keypress()

    if choice == "1":
        storage_table = 'LVS01'
        manageStorage(storage_table)
    elif choice == "2":
        storage_table = 'LVS02'
        manageStorage(storage_table)
    elif choice == "3":
        viewAllSideStorage()
        pressAnyKeyForMenu()  # Wait for keypress before going back to menu
    else:
        menu()  # Exit if no valid choice


def manageStorage(storage_table):
    console_clear()
    print(f"Managing {storage_table} (Press Enter to exit):")
    print("")
    print("1. Add stock from main storage")
    print("2. Remove stock to main storage")
    print("3. Add stock directly to storage") 
    print("")
    choice = get_keypress()

    if choice == "":
        machineSideStorage()

    if choice == "1":
        transferStock('products', storage_table)
    elif choice == "2":
        transferStock(storage_table, 'products')
    elif choice == "3":
        addStockDirectly(storage_table) 
    else:
        machineSideStorage() 


def transferStock(from_table, to_table):
    while True:
        product_code = input("Enter product code (or press Enter to exit): ").strip()
        if product_code == "":
            manageStorage()

        amount = input("Enter amount to transfer: ").strip()
        if amount == "":
            manageStorage()
        amount = int(amount)

        # Fetch current stock from source table
        cursor.execute(f"SELECT current_stock FROM {from_table} WHERE product_code = ?", (product_code.upper(),))
        result = cursor.fetchone()

        if result is None:
            print(f"Product with code {product_code} not found in {from_table}.")
            pressAnyKeyForMenu()
            continue 
        
        current_stock = result[0]

        if current_stock < amount:
            print(f"Not enough stock in {from_table}. Available: {current_stock}")
            pressAnyKeyForMenu()
            continue

        # take stock from source table
        new_stock_from = current_stock - amount
        cursor.execute(f"UPDATE {from_table} SET current_stock = ? WHERE product_code = ?", (new_stock_from, product_code.upper()))

        # add stock to destination table
        cursor.execute(f"SELECT current_stock FROM {to_table} WHERE product_code = ?", (product_code,))
        result = cursor.fetchone()

        if result:
            new_stock_to = result[0] + amount
            cursor.execute(f"UPDATE {to_table} SET current_stock = ? WHERE product_code = ?", (new_stock_to, product_code))
        else:
            cursor.execute(f"INSERT INTO {to_table} (product_name, product_code, ean, current_stock, location, supplier, status, unit_price, sale_price) SELECT product_name, product_code, ean, ?, location, supplier, status, unit_price, sale_price FROM {from_table} WHERE product_code = ?", (amount, product_code))

        conn.commit()
        print(f"Transferred {amount} units of {product_code} from {from_table} to {to_table}.")

    manageStorage()


def addStockDirectly(storage_table):
    while True:
        product_code = input("Enter product code (or press Enter to exit): ").strip()
        if product_code == "":
            manageStorage(storage_table)
            break

        amount = input("Enter amount to add: ").strip()
        if amount == "":
            manageStorage(storage_table)
            break
        amount = int(amount)

        # Check if the product exists
        cursor.execute("SELECT product_name, product_code, ean, location, supplier, status, unit_price, sale_price FROM PRODUCTS WHERE product_code = ?", (product_code.upper(),))
        product_info = cursor.fetchone()

        if product_info:
            # Product exists
            cursor.execute(
                f"INSERT INTO {storage_table} (product_name, product_code, ean, current_stock, location, supplier, status, unit_price, sale_price) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (*product_info[:3], amount, *product_info[3:])
            )
            conn.commit()  
            print(f"Added {amount} units of {product_code.upper()} to {storage_table}.")
        else:
            # Product doesn't exist
            print(f"Product with code {product_code.upper()} not found in PRODUCTS table. No stock added.")
            
    manageStorage(storage_table)




def viewAllSideStorage():
    console_clear()
    print("Viewing all side storages:")
    print("")

    for storage_table in ['LVS01', 'LVS02']: 
        print(f"--- {storage_table} ---")
        cursor.execute(f"SELECT product_name, product_code, current_stock FROM {storage_table}")
        products = cursor.fetchall()
        
        if products:
            for product in products:
                product_name, product_code, current_stock = product
                print(f"Product: {product_name}, Code: {product_code}, Stock: {current_stock}")
        else:
            print(f"No stock in {storage_table}.")
        
        print("")  # Space between

    print("End of side storage view.")


def newProduct():
    console_clear()
    print("New product (Type 'exit' to cancel):")
    print("")
    np_pname = input("Product name: ")
    if np_pname.lower() == "exit":
        menu()
    np_pcode = input("Product code: ")
    if np_pcode.lower() == "exit":
        menu()
    elif not np_pcode.isalpha():
        print("Invalid charater (A-Z only)")
        time.sleep(0.5)
        newProduct()
    np_ean = input("Product EAN (Enter = no EAN): ")
    if np_ean.lower() == "exit":
        menu()
    np_currentstock = input("Current product stock: ")
    if np_currentstock.lower() == "exit":
        menu()
    np_location = input("Location (press enter for no location): ")
    if np_location.lower() == "exit":
        menu()
    np_supplier = input("Product supplier (press enter for no supplier): ")
    if np_supplier.lower() == "exit":
        menu()
    np_unit_price = input("Unit price (from supplier): ")
    if np_unit_price.lower() == "exit":
        menu()
    np_sale_price = input("Sale price: ")
    if np_sale_price.lower() == "exit":
        menu()  
    status = input("Product status (A = Active, I = Inactive. this can be further specified later): ")
    if status.lower() == "exit":
        menu()
    elif status.lower() == "a":
        np_status = "Active"
    elif status.lower() == "i":
        np_status = "inactive"
    else:
        np_status = status
    cursor.execute("SELECT * FROM products WHERE product_code=?", (np_pcode,))
    check = cursor.fetchall()
    if check:
        print(f"Error: Product with product code {np_pcode} already exists")
        time.sleep(0.8)
        newProduct()
    else:
        writeToDB(np_pname, np_pcode, np_ean, np_currentstock, np_location, np_supplier, np_status, np_unit_price, np_sale_price)
        print(f"{np_pname} has been successfully added to StockFox")
        print("")
        print("Stockfox entry:")
        print(f"Name: {np_pname}, Code: {np_pcode}, EAN: {np_ean}, Stock: {np_currentstock}, Location: {np_location}")
        print(f"Supplier: {np_supplier}, Unit Price: {np_unit_price}, Sale Price: {np_sale_price} Status: {np_status}")
        print("")
        pressAnyKeyForMenu()

def editProduct():
    while True:
        try:
            console_clear()
            ep_pcode = input("Please input the product code or EAN for the product you want to edit (or press Enter to exit): ")
            danger = "drop"  # more flags can be added if required

            if ep_pcode == "":
                menu()
                return

            if ep_pcode.lower() == "sql":
                print(bcolors.WARNING + "WARNING: Custom SQL commands can be very dangerous. Only do this if you know what you're doing!" + bcolors.ENDC)
                while True:
                    custom_sql = input("SQL command (type 'exit' to go back to menu): ")
                    if custom_sql.lower() == "exit":
                        menu()
                        return
                    
                    if danger in custom_sql.lower():
                        danger_conf = input(f"Are you sure you want to run the SQL command '{custom_sql}'? (Y/N) ")
                        if danger_conf.lower() != "y":
                            print("Command cancelled.")
                            continue
                    
                    try:
                        cursor.execute(custom_sql)
                        result = cursor.fetchall()
                        print(result)
                    except Exception:
                        print("Invalid SQL query.")

            elif ep_pcode.lower() == "add ean":
                addEanToProduct()
                continue

            elif ep_pcode.lower() in ["export", "export db", "backup"]:
                backup_products_to_csv()
                continue

            elif ep_pcode.isdigit():
                cursor.execute("SELECT * FROM products WHERE ean=?", (ep_pcode.upper(),))
                result = cursor.fetchone()

                if not result:
                    print("Product not found. Try again.")
                    time.sleep(0.5)
                    continue

                status = result[7]
                status_display = (bcolors.OKGREEN + "██ ACTIVE" + bcolors.ENDC) if status.lower() == "active" else (bcolors.FAIL + "██ INACTIVE" + bcolors.ENDC if status.lower() == "inactive" else status)

                print(f"\n1. Product name: {result[1]}")
                print(f"2. Product code: {result[2]}")
                print(f"3. Product EAN: {result[3]}")
                print(f"4. Product location: {result[5]}")
                print(f"5. Product supplier: {result[6]}")
                print(f"6. Product status: {status_display}")
                print(f"7. Unit price: {result[8]}")
                print(f"8. Sale price: {result[9]}\n")

                while True:
                    try:
                        entryEdit = int(input("Enter which line you want to edit (or '0' to exit): "))
                        break
                    except ValueError:
                        print("Please input a number.")
                        continue

                if entryEdit == 0:
                    return

                if entryEdit == 1:
                    new_name = input(f"Please enter new product name (current: {result[1]}): ")
                    cursor.execute("UPDATE products SET product_name=? WHERE ean=?", (new_name, ep_pcode.upper()))
                    conn.commit()
                    print(f"Product name changed to {new_name} successfully")
                    time.sleep(0.5)
                elif entryEdit == 2:
                    new_pcode = input(f"Please enter new product code (current: {result[2]}): ")
                    cursor.execute("UPDATE products SET product_code=? WHERE ean=?", (new_pcode, ep_pcode.upper()))
                    conn.commit()
                    print(f"Product code changed to {new_pcode} successfully")
                    time.sleep(0.5)
                elif entryEdit == 3:
                    new_ean = input(f"Please enter new product EAN (current: {result[3]}): ")
                    cursor.execute("UPDATE products SET ean=? WHERE ean=?", (new_ean, ep_pcode.upper()))
                    conn.commit()
                    print(f"Product EAN changed to {new_ean} successfully")
                    time.sleep(0.5)
                elif entryEdit == 4:
                    new_location = input(f"Please enter new product location (current: {result[5]}): ")
                    cursor.execute("UPDATE products SET location=? WHERE ean=?", (new_location, ep_pcode.upper()))
                    conn.commit()
                    print(f"Product location changed to {new_location} successfully")
                    time.sleep(0.5)
                elif entryEdit == 5:
                    new_supplier = input(f"Please enter new product supplier (current: {result[6]}): ")
                    cursor.execute("UPDATE products SET supplier=? WHERE ean=?", (new_supplier, ep_pcode.upper()))
                    conn.commit()
                    print(f"Product supplier changed to {new_supplier} successfully")
                    time.sleep(0.5)
                elif entryEdit == 6:
                    ep_status = input(f"Please enter new product status (current: {status_display}, A=Active, I=Inactive, or custom): ")
                    new_status = "Active" if ep_status.lower() == "a" else "Inactive" if ep_status.lower() == "i" else ep_status
                    cursor.execute("UPDATE products SET status=? WHERE ean=?", (new_status, ep_pcode.upper()))
                    conn.commit()
                    status_display_confirmation = bcolors.OKGREEN + "██ ACTIVE" + bcolors.ENDC if new_status.lower() == "active" else bcolors.FAIL + "██ INACTIVE" + bcolors.ENDC if new_status.lower() == "inactive" else new_status
                    print(f"Product status changed to {status_display_confirmation} successfully")
                    time.sleep(0.5)
                elif entryEdit == 7:
                    new_unit_price = input(f"Please enter new product unit price (current: {result[8]}): ")
                    cursor.execute("UPDATE products SET unit_price=? WHERE ean=?", (new_unit_price, ep_pcode.upper()))
                    conn.commit()
                    print(f"Product unit price changed to {new_unit_price} successfully")
                    time.sleep(0.5)
                elif entryEdit == 8:
                    new_sale_price = input(f"Please enter new product sale price (current: {result[9]}): ")
                    cursor.execute("UPDATE products SET sale_price=? WHERE ean=?", (new_sale_price, ep_pcode.upper()))
                    conn.commit()
                    print(f"Product sale price changed to {new_sale_price} successfully")
                    time.sleep(0.5)
                else:
                    print("Invalid choice.")
                    time.sleep(1)

            else:
                cursor.execute("SELECT * FROM products WHERE product_code=?", (ep_pcode.upper(),))
                result = cursor.fetchone()

                if not result:
                    print("Product not found. Try again.")
                    time.sleep(0.5)
                    continue

                status = result[7]
                status_display = (bcolors.OKGREEN + "██ ACTIVE" + bcolors.ENDC) if status.lower() == "active" else (bcolors.FAIL + "██ INACTIVE" + bcolors.ENDC if status.lower() == "inactive" else status)

                print(f"\n1. Product name: {result[1]}")
                print(f"2. Product code: {result[2]}")
                print(f"3. Product EAN: {result[3]}")
                print(f"4. Product location: {result[5]}")
                print(f"5. Product supplier: {result[6]}")
                print(f"6. Product status: {status_display}")
                print(f"7. Unit price: {result[8]}")
                print(f"8. Sale price: {result[9]}\n")

                while True:
                    try:
                        entryEdit = int(input("Enter which line you want to edit (or '0' to exit): "))
                        break
                    except ValueError:
                        print("Please input a number.")
                        continue

                if entryEdit == 0:
                    return

                if entryEdit == 1:
                    new_name = input(f"Please enter new product name (current: {result[1]}): ")
                    cursor.execute("UPDATE products SET product_name=? WHERE product_code=?", (new_name, ep_pcode.upper()))
                    conn.commit()
                    print(f"Product name changed to {new_name} successfully")
                    time.sleep(0.5)
                elif entryEdit == 2:
                    new_pcode = input(f"Please enter new product code (current: {result[2]}): ")
                    cursor.execute("UPDATE products SET product_code=? WHERE product_code=?", (new_pcode, ep_pcode.upper()))
                    conn.commit()
                    print(f"Product code changed to {new_pcode} successfully")
                    time.sleep(0.5)
                elif entryEdit == 3:
                    new_ean = input(f"Please enter new product EAN (current: {result[3]}): ")
                    cursor.execute("UPDATE products SET ean=? WHERE product_code=?", (new_ean, ep_pcode.upper()))
                    conn.commit()
                    print(f"Product EAN changed to {new_ean} successfully")
                    time.sleep(0.5)
                elif entryEdit == 4:
                    new_location = input(f"Please enter new product location (current: {result[5]}): ")
                    cursor.execute("UPDATE products SET location=? WHERE product_code=?", (new_location, ep_pcode.upper()))
                    conn.commit()
                    print(f"Product location changed to {new_location} successfully")
                    time.sleep(0.5)
                elif entryEdit == 5:
                    new_supplier = input(f"Please enter new product supplier (current: {result[6]}): ")
                    cursor.execute("UPDATE products SET supplier=? WHERE product_code=?", (new_supplier, ep_pcode.upper()))
                    conn.commit()
                    print(f"Product supplier changed to {new_supplier} successfully")
                    time.sleep(0.5)
                elif entryEdit == 6:
                    ep_status = input(f"Please enter new product status (current: {status_display}, A=Active, I=Inactive, or custom): ")
                    new_status = "Active" if ep_status.lower() == "a" else "Inactive" if ep_status.lower() == "i" else ep_status
                    cursor.execute("UPDATE products SET status=? WHERE product_code=?", (new_status, ep_pcode.upper()))
                    conn.commit()
                    status_display_confirmation = bcolors.OKGREEN + "██ ACTIVE" + bcolors.ENDC if new_status.lower() == "active" else bcolors.FAIL + "██ INACTIVE" + bcolors.ENDC if new_status.lower() == "inactive" else new_status
                    print(f"Product status changed to {status_display_confirmation} successfully")
                    time.sleep(0.5)
                elif entryEdit == 7:
                    new_unit_price = input(f"Please enter new product unit price (current: {result[8]}): ")
                    cursor.execute("UPDATE products SET unit_price=? WHERE product_code=?", (new_unit_price, ep_pcode.upper()))
                    conn.commit()
                    print(f"Product unit price changed to {new_unit_price} successfully")
                    time.sleep(0.5)
                elif entryEdit == 8:
                    new_sale_price = input(f"Please enter new product sale price (current: {result[9]}): ")
                    cursor.execute("UPDATE products SET sale_price=? WHERE product_code=?", (new_sale_price, ep_pcode.upper()))
                    conn.commit()
                    print(f"Product sale price changed to {new_sale_price} successfully")
                    time.sleep(0.5)
                else:
                    print("Invalid choice.")
                    time.sleep(1)

        except Exception:
            print("Invalid product, try again.")
            time.sleep(0.5)



def viewProductDetails():
    print("View product details:")
    print("")
    while True:
        VPD_code = input("Enter product code or EAN (or press Enter to exit): ")
        try:
            if VPD_code == "":
                menu()

            elif VPD_code.isdigit():
                cursor.execute("SELECT * FROM products WHERE ean=?", (VPD_code,))
                result = cursor.fetchall()
                
                if result:
                    if len(result[0]) > 7: 
                        status = result[0][7]  
                        if status.lower() == "active":
                            status_display = bcolors.OKGREEN + "██ ACTIVE" + bcolors.ENDC
                        elif status.lower() == "inactive":
                            status_display = bcolors.FAIL + "██ INACTIVE" + bcolors.ENDC
                        else:
                            status_display = status

                        print("")
                        print(f"Product name: {result[0][1]}")  # Access first product
                        print(f"Product code: {result[0][2]}")
                        print(f"Product EAN: {result[0][3]}")
                        print(f"Stock (Main storage): {result[0][4]}")
                        print(f"Product location: {result[0][5]}")  # skipping stock
                        print(f"Product supplier: {result[0][6]}")
                        print(f"Product status: {status_display}")
                        print(f"Unit price (from {result[0][6]}): {result[0][8]}")
                        print(f"Sale price: {result[0][9]}")
                    else:
                        print("Product details are incomplete.")
                else:
                    print("Product not found.")
                    time.sleep(0.5)
                    viewProductDetails()
            
            else:
                cursor.execute("SELECT * FROM products WHERE product_code=?", (VPD_code.upper(),))
                result = cursor.fetchall()

                if result:
                    if len(result[0]) > 7:  
                        status = result[0][7] 
                        if status.lower() == "active":
                            status_display = bcolors.OKGREEN + "██ ACTIVE" + bcolors.ENDC
                        elif status.lower() == "inactive":
                            status_display = bcolors.FAIL + "██ INACTIVE" + bcolors.ENDC
                        else:
                            status_display = status

                        print("")
                        print(f"Product name: {result[0][1]}")
                        print(f"Product code: {result[0][2]}")
                        print(f"Product EAN: {result[0][3]}")
                        print(f"Product location: {result[0][5]}")  # skipping stock
                        print(f"Product supplier: {result[0][6]}")
                        print(f"Product status: {status_display}")
                        print("")
                    else:
                        print("Product details are incomplete.")
                else:
                    print("Product not found.")
                    time.sleep(0.5)
                    viewProductDetails()
            
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(0.5)
            viewProductDetails()

def removeProduct():
    console_clear()
    print("Remove product:")
    print("")
    rp_pcode = input("Enter the product code or EAN of the product you want to delete (or press Enter to cancel): ")

    if rp_pcode == "":
        menu()

    #wipe db function:
    elif rp_pcode.lower() == "drop table":
        the_choice = input("Are you sure? This action can NOT be undone! (Y/N) ")
        if the_choice.lower() == "y":
            print("")
            the_second_choice = input("This will quite literally remove everything. are you SURE you want to do this? (Y/N) ")
            if the_second_choice.lower() == "y":
                print("")
                the_last_choice = input("To confirm, please write 'I am fully aware this will delete the database' ")
                if the_last_choice.lower() == "i am fully aware this will delete the database":
                    cursor.execute("DROP TABLE products")
                    conn.commit()
                    for i in range(5):
                        console_clear()
                        print("Table dropped. This action requires a full restart of Stockfox. Please relaunch the program.")
                        print("")
                        print(f"Closing Stockfox in {5-i} seconds...")
                        time.sleep(1)
                    sys.exit()

                else:
                    removeProduct()
            else:
                removeProduct()
        else:
            removeProduct()

    try:
        if rp_pcode == "":
            menu()

        elif rp_pcode.isdigit():
            cursor.execute("SELECT product_name FROM products WHERE ean=?", (rp_pcode,))
            result = cursor.fetchone()
            
            if result:
                confirmation_delete = input(f"Are you sure you want to delete {result[0]}? (Y/N): ")
                if confirmation_delete.lower() == "y":
                    cursor.execute("DELETE FROM products WHERE ean=?", (rp_pcode,))
                    print("Product deleted")
                    conn.commit()  # Commit after delete
            else:
                print("Product not found.")
                time.sleep(0.5)
                removeProduct()
        
        else:
            cursor.execute("SELECT product_name FROM products WHERE product_code=?", (rp_pcode.upper(),))
            result = cursor.fetchone()

            if result:
                confirmation_delete = input(f"Are you sure you want to delete {result[0]}? (Y/N): ")
                if confirmation_delete.lower() == "y":
                    cursor.execute("DELETE FROM products WHERE product_code=?", (rp_pcode.upper(),))
                    print(f"{result[0]} was deleted")
                    conn.commit()  # Commit after delete
                    time.sleep(0.5)
                    menu()
                else:
                    removeProduct()
            else:
                print("Product not found.")
                time.sleep(0.5)
                removeProduct()
        
    except Exception as e:
        print(f"An error occurred: {e}")



def settings():
    console_clear()
    print("---------- StockFox ----------")
    print("                  ____")
    print("          |\/|  /\  /")
    print("       .__.. \_/  \/")
    print("        \____/_ __/  ") 
    print("           /_/_/")
    print("")
    print("2024 © Lien Vending Solutions")
    print("Version Beta 1.3")
    print("Made in Norway ♥")
    print("")
    print("Support: stockfox@lienvending.solutions")
    print("")
    pressAnyKeyForMenu()

menu()