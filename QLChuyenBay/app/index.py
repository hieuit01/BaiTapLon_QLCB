import dao
from flask import Flask, render_template, request, redirect, url_for, jsonify
from app import app, db


# Trang chủ
@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    # with app.app_context():
    #     db.create_all()
    app.run(debug=True)
