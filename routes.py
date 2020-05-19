from flask import Flask, render_template
import sqlite3

app = Flask(__name__)


@app.route('/')
def home():
    return render_template("home.html", page_title="WELCOME TO FH4 CARS")


if __name__ == "__main__":
    app.run(debug=True, port=1111)
