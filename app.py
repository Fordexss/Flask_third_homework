import sqlite3

from flask import Flask, g, render_template, request, redirect, url_for

app = Flask('Oderman', template_folder="templates", static_folder="static")
DATABASE = 'oderman_db.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        create_order_table(db)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def create_order_table(db):
    db.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        phone_number TEXT NOT NULL,
        address TEXT NOT NULL,
        pizza_type TEXT NOT NULL
    )
    ''')
    db.commit()

    db.commit()


menu_items = [
    {"name": "Маргарита", "description": "Томатний соус, моцарела, базилік", "price": 100},
    {"name": "Пепероні", "description": "Томатний соус, пепероні, моцарела", "price": 120},
    {"name": "Гавайська", "description": "Томатний соус, курка, ананас, моцарела", "price": 130},
    {"name": "Чотири сири", "description": "Томатний соус, гауда, пармезан, дор-блю, моцарела", "price": 150},
    {"name": "Вегетаріанська", "description": "Томатний соус, гриби, перець, помідор, моцарела", "price": 110},
]


@app.route('/')
@app.route('/index')
def index():
    pizza_name = "Oderman"
    return render_template("index.html", pizza_name=pizza_name)


@app.route('/menu')
def menu():
    return render_template("menu.html", menu_items=menu_items)


@app.route('/aboutUs')
def about_us():
    return render_template('about_us.html', title='Про нас', header='Інформація про нас')


@app.route('/order', methods=['GET', 'POST'])
def order():
    if request.method == 'POST':
        first_name = request.form.get('first_name', '')
        last_name = request.form.get('last_name', '')
        phone_number = request.form.get('phone_number', '')
        address = request.form.get('address', '')
        pizza_type = request.form.get('pizza_type', '')

        if first_name and last_name and phone_number and address and pizza_type:
            db = get_db()
            db.execute(
                'INSERT INTO orders (first_name, last_name, phone_number, address, pizza_type) VALUES (?, ?, ?, ?, ?)',
                (first_name, last_name, phone_number, address, pizza_type))
            db.commit()

            return redirect(url_for('orders'))

    return render_template('order_form.html')


@app.route('/orders')
def orders():
    db = get_db()
    cur = db.execute('SELECT * FROM orders ORDER BY id DESC')
    orders = cur.fetchall()
    return render_template('orders.html', orders=orders)


if __name__ == "__main__":
    with app.app_context():
        get_db()
    app.run(debug=True)
