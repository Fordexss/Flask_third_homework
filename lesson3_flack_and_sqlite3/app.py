import sqlite3
from flask import Flask, g, render_template, request

app = Flask(__name__)

DATABASE = 'test_db.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def create_db():
    cr = sqlite3.connect(DATABASE)
    cr.execute("""
        CREATE TABLE IF NOT EXISTS participants
            (name VARCHAR(128), email VARCHAR(128), city INT, order_name VARCHAR(128), phone VARCHAR(32)) 
    """)

    cr.execute("""
        CREATE TABLE IF NOT EXISTS cities
            (id INT, name VARCHAR(128))
    """)

    cr.executemany("INSERT INTO cities (id, name) VALUES (?, ?)",
                   [(1, 'Kyiv'), (2, 'Lviv'), (3, 'Khmelnitskiy'), (4, 'Kharkiv'), (5, 'Dnipro')])

    cr.commit()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
    return render_template("index.html")


@app.route('/join/', methods=['GET', 'POST'])
def join():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        city = request.form.get("city")
        phone = request.form.get("phone")
        order = request.form.get("order")

        try:
            cr = get_db()

            cities_cursor = cr.execute("SELECT id, name FROM cities")
            cities = {row[0]: row[1] for row in cities_cursor.fetchall()}

            # print(f"Отримані міста: {cities}")

            cr.execute("""
                INSERT INTO participants (name, email, city, phone, order_name) VALUES (?,?,?,?,?)
            """, (name, email, city, phone, order))

            cr.commit()

            return render_template("index.html", cities=cities)

        except Exception as e:
            print(e)
            return render_template("index.html", cities={})

    else:
        cr = get_db().cursor()
        cr.execute("SELECT id, name FROM cities")
        cities = {row[0]: row[1] for row in cr.fetchall()}

        # Виведення для перевірки
        # print(f"Отримані міста: {cities}")

        return render_template("join.html", cities=cities)


@app.route('/participants/')
def participants():
    cr = get_db().cursor()
    cr.execute("""
        SELECT DISTINCT participants.name, participants.email, cities.name, participants.phone, participants.order_name
        FROM participants
        INNER JOIN cities ON participants.city = cities.id
    """)
    data = cr.fetchall()
    return render_template("participants.html", participants=data)


if __name__ == "__main__":
    create_db()
    app.run(debug=False)