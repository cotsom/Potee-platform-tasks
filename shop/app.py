from functools import wraps
import os
import pymongo
from redis import Redis
from bson.objectid import ObjectId
from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session


def mongoConnect():
    db_client = pymongo.MongoClient(
        host="mongo",
        username=os.getenv("MONGO_USER"),
        password=os.getenv("MONGO_PASS"),
    )
    current_db = db_client["shop"]
    return current_db


app = Flask(__name__)
app.secret_key = "g8y348f3h4f34jf93ij4g3u49gh3487fh34fj8347hfg3487fh348jf34hf837fg"

app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_USE_SIGNER"] = True
app.config["SESSION_REDIS"] = Redis(
    host="redis", password="eYVX7EwVmmxKPCDmwMtyKVge8oLd2t81"
)
server_session = Session(app)


current_db = mongoConnect()
products_collection = current_db["products"]
transactions_collection = current_db["transactions"]
users_collection = current_db["users"]


def auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            session["user"] = False
        return f(*args, **kwargs)

    return decorated_function


def purchase(product_id, user_login, product_tag):
    user = users_collection.find_one({"login": user_login})
    product = products_collection.find_one({"product_id": int(product_id)})
    print(user, product)
    if user["balance"] < product["cost"]:
        new_transaction = {"product": product_id, "user": user_login, "status": False, "product_tag": product_tag}
    else:
        new_transaction = {"product": product_id, "user": user_login, "status": True, "product_tag": product_tag}
        new_balance = user["balance"] - product["cost"]
        users_collection.update_one(
            {"login": session["user"], "balance": user["balance"]},
            {"$set": {"balance": new_balance}},
        )
        print(users_collection.find_one({"login": session["user"]}))
    return transactions_collection.insert_one(new_transaction).inserted_id


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        current_db = mongoConnect()
        users_collection = current_db["users"]

        action = request.form["action"]
        login = request.form["login"]
        password = request.form["passwd"]
        card = request.form.get("card")

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
                "bank_card_details": card
            }
            ins_result = users_collection.insert_one(new_user)
        elif action == "signin":
            if users_collection.find_one({"$where": "this.login == '" + login + "' && this.password == '" + password + "'"}):
                session["user"] = login
                return redirect(url_for("shop"))

    return render_template("index.html")


@auth
@app.route("/shop", methods=["GET", "POST"])
def shop():
    is_user = session.get("user", False)
    if not (is_user):
        return redirect(url_for("index"))

    current_db = mongoConnect()
    users_collection = current_db["users"]

    current_user_balance = users_collection.find_one({"login": session["user"]})[
        "balance"
    ]
    current_username = users_collection.find_one({"login": session["user"]})["login"]

    if request.method == "POST":
        product_id = request.form["product-id"]
        print(product_id, session["user"])
        # payment_id = purchase(product_id, session['user'])

        return redirect(url_for(f"approve", product_id=product_id))

    return render_template(
        "shop.html", balance=current_user_balance, username=current_username
    )


@auth
@app.route("/approve", methods=["GET", "POST"])
def approve():
    product_id = int(request.args.get("product_id"))
    product_title = products_collection.find_one({"product_id": product_id})["title"]

    if request.method == "POST":
        user_answer = request.form["buy"]
        if user_answer == "yes":
            product_tag = request.form["tag"]
            payment_id = purchase(product_id, session["user"], product_tag)
            session['product_id'] = product_id
            return redirect(url_for(f"buy", payment_id=payment_id))
        elif user_answer == "no":
            return redirect(url_for("shop"))
    return render_template("approve.html", product_title=product_title)


@auth
@app.route("/buy", methods=["GET", "POST"])
def buy():
    payment_id = request.args.get("payment_id")
    product_id = session['product_id']

    transaction = transactions_collection.find_one({"_id": ObjectId(payment_id)})
    user = users_collection.find_one({"login": session["user"]})
    if transaction["status"]:
        user["available_product"].append(product_id)
        users_collection.update_one(
            {"login": session["user"]},
            {"$set": {"available_product": user["available_product"]}},
        )
        print(user)
    else:
        return render_template("unsuccessful_purchase.html")

    return render_template("successful_purchase.html")


@auth
@app.route("/inventory")
def inventory():
    is_user = session.get("user", False)
    if not (is_user):
        return redirect(url_for("index"))
    current_user_balance = users_collection.find_one({"login": session["user"]})[
        "balance"
    ]
    user = users_collection.find_one({"login": session["user"]})
    username = user["login"]
    user_products = user["available_product"]
    card_details = user['bank_card_details']
    products = products_collection.find({"product_id": {"$in": user_products}})

    print(user_products)
    print(products)

    return render_template(
        "inventory.html",
        balance = current_user_balance,
        username = username,
        products = products,
        card = card_details
    )

@auth
@app.route("/check", methods=["GET", "POST"])
def check():
    is_user = session.get("user", False)
    if not (is_user):
        return redirect(url_for("index"))
    current_user_balance = users_collection.find_one({"login": session["user"]})[
        "balance"
    ]
    user = users_collection.find_one({"login": session["user"]})
    username = user["login"]

    product_name = ''
    owner = ''
    status = ''
    product_tag = ''
    if request.method == "POST":
        transaction_id = request.form["transaction"]
        if len(transaction_id) == 24:
            transaction = transactions_collection.find_one({"_id": ObjectId(transaction_id)})
            if transaction:
                product_name = products_collection.find_one({"product_id": transaction['product']})['title']
                owner = transaction['user']
                status = transaction['status']
                product_tag = transaction['product_tag']

    return render_template("find.html", balance = current_user_balance,
        username = username, product_name=product_name, owner=owner, status=status, product_tag=product_tag)

@auth
@app.route("/delete")
def delete():
    users_collection.delete_one({"login": session["user"]})
    session["user"] = ""

    return redirect(url_for(f"index"))


@auth
@app.route("/logout")
def logout():
    session.pop("user", default=None)
    return redirect(url_for(f"index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000", debug=False)
