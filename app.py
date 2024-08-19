from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            account_number TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            balance REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        account_number = request.form['account_number']
        name = request.form['name']
        balance = float(request.form['balance'])

        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE account_number = ?', (account_number,))
        existing_account = cursor.fetchone()

        if existing_account:
            flash('Account number already exists! Please try again.', 'error')
        else:
            cursor.execute('INSERT INTO accounts (account_number, name, balance) VALUES (?, ?, ?)',
                           (account_number, name, balance))
            conn.commit()
            flash('Account created successfully!', 'success')
        conn.close()
        return redirect(url_for('index'))
    return render_template('create_account.html')

@app.route('/view_account', methods=['GET', 'POST'])
def view_account():
    account = None
    if request.method == 'POST':
        account_number = request.form['account_number']

        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE account_number = ?', (account_number,))
        account = cursor.fetchone()
        conn.close()

        if not account:
            flash('Account not found!', 'error')
        else:
            account = {'account_number': account[0], 'name': account[1], 'balance': account[2]}

    return render_template('view_account.html', account=account)

@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if request.method == 'POST':
        account_number = request.form['account_number']
        amount = float(request.form['amount'])

        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE account_number = ?', (account_number,))
        account = cursor.fetchone()

        if account:
            new_balance = account[2] + amount
            cursor.execute('UPDATE accounts SET balance = ? WHERE account_number = ?',
                           (new_balance, account_number))
            conn.commit()
            flash(f'Successfully deposited {amount}!', 'success')
        else:
            flash('Account not found!', 'error')
        conn.close()
        return redirect(url_for('index'))
    return render_template('deposit.html')

@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    if request.method == 'POST':
        account_number = request.form['account_number']
        amount = float(request.form['amount'])

        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE account_number = ?', (account_number,))
        account = cursor.fetchone()

        if account:
            if amount > account[2]:
                flash('Insufficient balance!', 'error')
            else:
                new_balance = account[2] - amount
                cursor.execute('UPDATE accounts SET balance = ? WHERE account_number = ?',
                               (new_balance, account_number))
                conn.commit()
                flash(f'Successfully withdrew {amount}!', 'success')
        else:
            flash('Account not found!', 'error')
        conn.close()
        return redirect(url_for('index'))
    return render_template('withdraw.html')

if __name__ == '__main__':
    app.run(debug=True)
