import sqlite3
import pandas as pd
import matplotlib.pyplot as plt 
import json

from flask import Flask, render_template, request,redirect,url_for

# Create Database
conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL,
    category TEXT,
    description TEXT,
    date TEXT
)
""")

conn.commit()
conn.close()


# Add Expense
def add_expense():
    amount = float(input("Amount: "))
    category = input("Category: ")
    description = input("Description: ")
    date = input("Date: ")

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO expenses(amount, category, description, date) VALUES (?, ?, ?, ?)",
        (amount, category, description, date)
    )

    conn.commit()
    conn.close()

    print("Expense Added!")


# View Expenses
def view_expenses():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses")
    records = cursor.fetchall()

    if records:
        print("\nID | Amount | Category | Description | Date")
        print("-" * 50)

        for row in records:
            print(row)
    else:
        print("No expenses found!")

    conn.close()


# Total Expense
def total_expense():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(amount) FROM expenses")
    total = cursor.fetchone()[0]

    if total is None:
        total = 0

    print("Total Expense:", total)

    conn.close()


# Pie Chart
def show_chart():
    conn = sqlite3.connect("expenses.db")

    df = pd.read_sql_query(
        "SELECT * FROM expenses",
        conn
    )

    conn.close()

    if df.empty:
        print("No expenses found!")
        return

    category_total = df.groupby("category")["amount"].sum()

    category_total.plot(
        kind="pie",
        autopct="%1.1f%%"
    )

    plt.title("Expense Distribution")
    plt.ylabel("")
    plt.show()


# Delete Expense
def delete_expense():
    expense_id = int(
        input("Enter Expense ID to delete: ")
    )

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM expenses WHERE id = ?",
        (expense_id,)
    )

    if cursor.rowcount > 0:
        print("Expense Deleted!")
    else:
        print("Expense ID Not Found!")

    conn.commit()
    conn.close()


# Search Expense
def search_expense():
    category = input(
        "Enter Category to Search: "
    )

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM expenses WHERE category = ?",
        (category,)
    )

    records = cursor.fetchall()

    if records:
        for row in records:
            print(row)
    else:
        print("No matching expenses found!")

    conn.close()


# Edit Expense
def edit_expense():
    expense_id = int(
        input("Enter Expense ID to edit: ")
    )

    amount = float(
        input("New Amount: ")
    )

    category = input(
        "New Category: "
    )

    description = input(
        "New Description: "
    )

    date = input(
        "New Date: "
    )

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE expenses
    SET amount = ?,
        category = ?,
        description = ?,
        date = ?
    WHERE id = ?
    """,
    (
        amount,
        category,
        description,
        date,
        expense_id
    ))

    if cursor.rowcount > 0:
        print("Expense Updated!")
    else:
        print("Expense ID Not Found!")

    conn.commit()
    conn.close()


# Budget Alert
def budget_alert():
    budget = float(
        input("Enter Monthly Budget: ")
    )

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT SUM(amount) FROM expenses"
    )

    total = cursor.fetchone()[0]

    if total is None:
        total = 0

    print("Current Expense:", total)

    if total > budget:
        print("⚠ Budget Exceeded!")
    else:
        print(
            "✅ Budget Remaining:",
            budget - total
        )

    conn.close()
  

def get_dashboard_data():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(amount) FROM expenses WHERE type='Income'")
    total_income = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(amount) FROM expenses WHERE type='Expense'")
    total_expense = cursor.fetchone()[0] or 0

    balance = total_income - total_expense

    conn.close()

    return total_income, total_expense, balance
  
conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()

cursor.execute("""
SELECT category, SUM(amount)
FROM expenses
WHERE type='Expense'
GROUP BY category
""")

data = cursor.fetchall()

labels = [row[0] for row in data]
values = [row[1] for row in data]

conn.close()

return render_template(
    "dashboard.html",
     income=income,
    expense=expense,
    balance=balance,
    labels=json.dumps(labels),
    values=json.dumps(values)
)

# Main Menu
while True:
    print("\n===== Expense Tracker =====")
    print("1. Add Expense")
    print("2. View Expenses")
    print("3. Total Expense")
    print("4. Show Chart")
    print("5. Delete Expense")
    print("6. Search Expense")
    print("7. Edit Expense")
    print("8. Budget Alert")
    print("9. Exit")

    choice = input("Enter Choice: ")

    if choice == "1":
        add_expense()

    elif choice == "2":
        view_expenses()

    elif choice == "3":
        total_expense()

    elif choice == "4":
        show_chart()

    elif choice == "5":
        delete_expense()

    elif choice == "6":
        search_expense()

    elif choice == "7":
        edit_expense()

    elif choice == "8":
        budget_alert()

    elif choice == "9":
        print("Thank you for using Expense Tracker!")
        break

    else:
        print("Invalid Choice!")