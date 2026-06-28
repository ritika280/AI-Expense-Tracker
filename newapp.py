from flask import Flask, render_template, request, redirect, Response
import sqlite3
import json
import csv
from ai import analyze_expenses 
from gemini_ai import analyze_expenses,ask_ai
from gemini_ai import ask_ai
app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("expenses.db")
    return conn

@app.route("/")
def home():

    conn = get_db()
    cursor = conn.cursor()

    search = request.args.get("search")

    if search:
        cursor.execute(
            "SELECT * FROM expenses WHERE category LIKE ?",
            ('%' + search + '%',)
        )
    else:
        cursor.execute("SELECT * FROM expenses")

    expenses = cursor.fetchall()

    cursor.execute("SELECT SUM(amount) FROM expenses")
    total = cursor.fetchone()[0]

    if total is None:
        total = 0

    cursor.execute("SELECT COUNT(DISTINCT category) FROM expenses")
    categories = cursor.fetchone()[0]
    cursor.execute("""
    SELECT category, SUM(amount)
    FROM expenses
    GROUP BY category
""")

    chart_data = cursor.fetchall() 
    conn.close()

    return render_template(
        "home.html",
        expenses=expenses,
        total=total,
        categories=categories,
        chart_data=chart_data
    )


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        amount = request.form["amount"]
        description = request.form["description"]
        category = request.form["category"]
        date = request.form["date"]
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO expenses ( amount, category,description, date) VALUES (?, ?, ?, ?)", ( amount, category, description, date))
        conn.commit()
        conn.close()

        return redirect("/")
    return render_template("add_expense.html")


@app.route("/delete/<int:id>")
def delete(id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM expenses WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":

        amount = request.form["amount"]
        category = request.form["category"]
        description = request.form["description"]
        date = request.form["date"]

        cursor.execute("""
        UPDATE expenses
        SET amount=?,
            category=?,
            description=?,
            date=?
        WHERE id=?
        """,
        (amount, category, description, date, id))

        conn.commit()
        conn.close()

        return redirect("/")

    cursor.execute(
        "SELECT * FROM expenses WHERE id=?",
        (id,)
    )

    expense = cursor.fetchone()

    conn.close()

    return render_template(
        "edit_expense.html",
        expense=expense
    )
    
@app.route("/dashboard")
def dashboard():


    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(amount) FROM expenses")
    expense = cursor.fetchone()[0] or 0 

    total_income = 0

    total_expense = expense
    balance = total_income - total_expense 

    # Pie Chart Data
    cursor.execute("""
        SELECT category, SUM(amount)
        FROM expenses
        GROUP BY category
    """)

    data = cursor.fetchall()

    labels = [row[0] for row in data]
    values = [row[1] for row in data]

  

    cursor.execute("SELECT COUNT(*) FROM expenses")
    total_transactions = cursor.fetchone()[0] 

    # Monthly Expense Chart
    cursor.execute("""
SELECT substr(date, 6, 2), SUM(amount)
FROM expenses
GROUP BY substr(date, 6, 2)
ORDER BY substr(date, 6, 2)
""")

    monthly = cursor.fetchall()

    months = [row[0] for row in monthly]
    monthly_values = [row[1] for row in monthly]

# Recent Transactions
    cursor.execute("""
    SELECT date, description, category, amount
    FROM expenses
    ORDER BY id DESC
    LIMIT 5
""")
    
    recent = cursor.fetchall() 
    
    conn.close() 
    
    return render_template(
    "dashboard.html",
    income=total_income,
    expense=total_expense,
    balance=balance,
    total_transactions=total_transactions,
    labels=json.dumps(labels),
    values=json.dumps(values),
    months=json.dumps(months),
    monthly_values=json.dumps(monthly_values),
    recent=recent
)
    
@app.route("/reports")
def reports():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(amount) FROM expenses")
    total = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM expenses")
    transactions = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT category) FROM expenses")
    categories = cursor.fetchone()[0]

    cursor.execute("""
    SELECT category, SUM(amount)
    FROM expenses
    GROUP BY category
    ORDER BY SUM(amount) DESC
    """)

    report = cursor.fetchall()

    conn.close()

    return render_template(
        "reports.html",
        total=total,
        transactions=transactions,
        categories=categories,
        report=report
    )

@app.route("/export/csv")
def export_csv():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, amount, category, description, date
    FROM expenses
    """)

    rows = cursor.fetchall()
    conn.close()
    class Echo:
        def write(self, value):
            return value
   
    def generate():

        data = csv.writer(Echo())

        yield data.writerow([
            "ID",
            "Amount",
            "Category",
            "Description",
            "Date"
        ])

        for row in rows:
            yield data.writerow(row)


    return Response(
        generate(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=expenses.csv"
        }
    )

@app.route("/ai-analysis")
def ai_analysis():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT amount, category, description, date
    FROM expenses
    """)

    expenses = cursor.fetchall()

    conn.close()

    result = analyze_expenses(expenses)

    return render_template(
        "ai.html",
        result=result
    )

@app.route("/chat", methods=["GET", "POST"])
def chat():

    answer = ""

    if request.method == "POST":

        question = request.form["question"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT amount, category, description, date
        FROM expenses
        """)

        expenses = cursor.fetchall()

        conn.close()

        answer = ask_ai(question, expenses)

    return render_template(
        "chat.html",
        answer=answer
    )
if __name__ == "__main__":
    app.run(debug=True)