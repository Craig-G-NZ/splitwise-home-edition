import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__, static_folder='css')


# Database path
db_path = 'db/expenses.db'

# Check if the database exists and create tables if necessary
def initialize_database():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create the 'expenses' table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (
                      id INTEGER PRIMARY KEY,
                      description TEXT,
                      amount REAL,
                      paid_by TEXT,
                      split_with TEXT,
                      is_equal_split INTEGER,
                      date DATE DEFAULT CURRENT_TIMESTAMP)''')  # Add a date column

    # Create a new table for transaction history
    cursor.execute('''CREATE TABLE IF NOT EXISTS transaction_history (
                      id INTEGER PRIMARY KEY,
                      description TEXT,
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')

    conn.commit()
    conn.close()

# Initialize the database
initialize_database()

# Check if the 'templates' directory exists, create it if not
templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
if not os.path.exists(templates_dir):
    os.makedirs(templates_dir)

# List of HTML files to check and copy if not found
html_files = ['index.html', 'edit.html', 'delete.html']

# Function to check and copy HTML files if not found
def check_and_copy_html_files():
    for html_file in html_files:
        src_path = os.path.join('docker_app_templates', html_file)
        dest_path = os.path.join(templates_dir, html_file)

        if not os.path.exists(dest_path):
            print(f"Copying {html_file} from Docker app...")
            shutil.copy(src_path, dest_path)

# Call the function to check and copy HTML files
check_and_copy_html_files()


# Calculate balances
def calculate_balances():
    balances = {}
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM expenses')

    for row in cursor.fetchall():
        id, description, amount, paid_by, split_with, is_equal_split,date = row
        if paid_by not in balances:
            balances[paid_by] = 0
        if split_with not in balances:
            balances[split_with] = 0

        if is_equal_split:
            # Equal split, subtract half from each user's balance
            balances[paid_by] -= amount / 2
            balances[split_with] += amount / 2
        else:
            # Not equal split
            balances[paid_by] -= amount
            balances[split_with] += amount

    conn.close()
    return balances

@app.route('/')
def index():
    balances = calculate_balances()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM expenses')
    expenses = cursor.fetchall()

    cursor.execute('SELECT * FROM transaction_history ORDER BY timestamp DESC')
    transaction_history = cursor.fetchall()

    conn.close()

    # Sort expenses by the first element (ID column) in descending order
    sorted_expenses = sorted(expenses, key=lambda x: x[0], reverse=True)

    return render_template('index.html', expenses=sorted_expenses, balances=balances, transaction_history=transaction_history)

@app.route('/add_expense', methods=['POST'])
def add_expense():
    try:
        description = request.form.get('description')
        amount = float(request.form.get('amount'))
        paid_by = request.form.get('paid_by')
        split_with = request.form.get('split_with')
        is_equal_split = request.form.get('is_equal_split') == 'on'
        date = request.form.get('date')  # Get the date from the form

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('INSERT INTO expenses (description, amount, paid_by, split_with, is_equal_split, date) VALUES (?, ?, ?, ?, ?, ?)',
                       (description, amount, paid_by, split_with, is_equal_split, date))  # Insert the date into the database

        cursor.execute('INSERT INTO transaction_history (description) VALUES (?)', (f'Added expense: {description}',))

        conn.commit()
        conn.close()
    except Exception as e:
        print("Error adding expense to database:", str(e))

    return redirect(url_for('index'))

@app.route('/edit/<int:index>', methods=['GET', 'POST'])
def edit_expense(index):
    if request.method == 'POST':
        new_description = request.form['description']
        new_amount = float(request.form['amount'])
        new_paid_by = request.form['paid_by']
        new_split_with = request.form['split_with']
        new_is_equal_split = request.form.get('is_equal_split') == 'on'
        new_date = request.form['date']  # Get the date from the form

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('UPDATE expenses SET description=?, amount=?, paid_by=?, split_with=?, is_equal_split=?, date=? WHERE id=?',
                       (new_description, new_amount, new_paid_by, new_split_with, new_is_equal_split, new_date, index))

        cursor.execute('INSERT INTO transaction_history (description) VALUES (?)', (f'Edited expense: {new_description}',))

        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM expenses WHERE id=?', (index,))
    expense = cursor.fetchone()
    conn.close()

    return render_template('edit.html', expense=expense)

@app.route('/delete/<int:index>', methods=['POST', 'GET'])
def delete_expense(index):
    if request.method == 'POST':
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM expenses WHERE id=?', (index,))
        cursor.execute('INSERT INTO transaction_history (description) VALUES (?)', (f'Deleted expense: ID {index}',))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))
    
    return redirect(url_for('index'))

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM expenses WHERE id=?', (index,))
    expense = cursor.fetchone()
    conn.close()

    return render_template('delete.html', expense=expense)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
