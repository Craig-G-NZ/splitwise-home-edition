import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
import json

app = Flask(__name__, static_folder='css')

# Database path
db_path = 'data/expenses.db'  # Updated database path

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

# Check for the config file in the 'data' directory
config_file_path = os.path.join('data', 'config.json')  # Updated config file path

if not os.path.exists(config_file_path):
    # Handle the case where the config file is not found
    print("Config file not found. Please create the config file in the 'data' directory.")
    exit()

# Load configuration from /app/data/config.json
try:
    with open(config_file_path, 'r') as config_file:
        config_data = json.load(config_file)
        print("Loaded configuration from config.json:", config_data)
except Exception as e:
    print(f"Error loading configuration from config.json: {str(e)}")
    exit()

# Calculate balances
def calculate_balances():
    balances = {}
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM expenses')

    for row in cursor.fetchall():
        id, description, amount, paid_by, split_with, is_equal_split, date = row
        balances.setdefault(paid_by, 0)
        balances.setdefault(split_with, 0)

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

    return render_template('index.html', expenses=sorted_expenses, balances=balances, transaction_history=transaction_history, expense={}, website_title=config_data['website_title'], website_name=config_data['website_name'])

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

@app.route('/data/<path:filename>')
def serve_parameters(filename):
    if filename == 'config.json':
        return jsonify(names=config_data.get('names', []))
    else:
        return send_from_directory('data', filename)

    
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

    return render_template('edit.html', expense=expense, website_title=config_data['website_title'], website_name=config_data['website_name'])

@app.route('/delete/<int:index>', methods=['POST'])
def delete_expense(index):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM expenses WHERE id=?', (index,))
    cursor.execute('INSERT INTO transaction_history (description) VALUES (?)', (f'Deleted expense: ID {index}',))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
