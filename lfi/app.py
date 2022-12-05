from functools import wraps
import io
import os
import pymongo
from redis import Redis
from flask import (
    Flask,
    redirect,
    render_template,
    render_template_string,
    request,
    session,
    url_for,
)

import requests
from flask_session import Session


app = Flask(__name__)
app.secret_key = "g8y348f3h4f34jf93ij4g3u49gh3487fh34fj8347hfg3487fh348jf34hf837fg"

app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_USE_SIGNER"] = True
app.config["SESSION_REDIS"] = Redis(
    host="redis", password="eYVX7EwVmmxKPCDmwMtyKVge8oLd2t81"
)
server_session = Session(app)


def mongoConnect():
    db_client = pymongo.MongoClient(
        host="mongo",
        username=os.getenv("MONGO_USER"),
        password=os.getenv("MONGO_PASS"),
    )
    current_db = db_client["shop"]
    return current_db


def auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            session["user"] = False
        return f(*args, **kwargs)

    return decorated_function


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        current_db = mongoConnect()
        users_collection = current_db["users"]

        action = request.form["action"]
        login = request.form["login"]
        password = request.form["passwd"]

        if action == "signup":
            if users_collection.find_one({"login": login}):
                if users_collection.find_one({"login": login})["login"] == "admin":
                    error_text = "you cannot have a login as the main user and owner of this store"
                    return render_template("index.html", error_text=error_text)
                error_text = "This user is already exist"
                return render_template("index.html", error_text=error_text)

            new_user = {
                "login": login,
                "password": password,
                "balance": 100,
                "available_product": [],
            }
            ins_result = users_collection.insert_one(new_user)
        elif action == "signin":
            if users_collection.find_one(
                {
                    "$where": "this.login == '"
                    + login
                    + "' && this.password == '"
                    + password
                    + "'"
                }
            ):
                session["user"] = login

                return redirect(url_for("talks"))

    return render_template("index.html")


@auth
@app.route("/talks", methods=["GET", "POST"])
def talks():
    user = session.get("user", False)
    if not user:
        return redirect(url_for("index"))
    return render_template("talks.html", username=user)


@auth
@app.route("/guest-ticket", methods=["GET", "POST"])
def guest():
    if request.method == "POST":
        session_cookie = request.cookies.get("session")

        s = requests.Session()
        s.cookies.set("session", session_cookie)
        product_id = request.form["product-id"]
        s.get(f"http://shop:5000/approve", params={"product_id": product_id})
        s.post(
            f"http://shop:5000/approve",
            data={"buy": "yes"},
            params={"product_id": product_id},
        )

    return render_template("guest.html")


@auth
@app.route("/speaker-ticket", methods=["GET", "POST"])
def speaker():
    if request.method == "POST":
        session_cookie = request.cookies.get("session")

        s = requests.Session()
        s.cookies.set("session", session_cookie)
        product_id = request.form["product-id"]
        s.get(f"http://shop:5000/approve", params={"product_id": product_id})
        s.post(
            f"http://shop:5000/approve",
            data={"buy": "yes"},
            params={"product_id": product_id},
        )  

    return render_template("speaker.html")


def replace(filename: str):
    filename = filename.encode()
    for symbol in [b"../", b"..", b"\x00"]:
        filename = filename.replace(symbol, b"")
        print(filename)
    return filename.decode()


@app.route("/images")
def qwe():
    filename = request.args.get("file")
    safe_filename = replace(filename)
    filename = "static/" + safe_filename
    if os.path.exists(filename) and os.path.isfile(filename):
        with io.open(filename, "rb") as f:
            file = f.read()
    else:
        file = f"Файл {filename} не найден"

    return file


@app.errorhandler(404)
def page_not_found(e):
    route = request.path.replace("/", "")
    template = """{%% extends "notFoundPage.html" %%}
    {%% block content %%}
        <div class="text">
            <h1>404 Error</h1>  
        <h2>Couldn't launch :(</h2>
            <h3>Page %s Not Found</h3> 
        </div>
    {%% endblock %%}""" % (
        route
    )
    return render_template_string(template), 404

@auth
@app.route("/logout")
def logout():
    session.pop("user", default=None)
    return redirect(url_for(f"index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000", debug=False)
