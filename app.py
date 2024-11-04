from flask import Flask
from flask import abort, make_response, redirect, render_template, request, session
import config, db, forum, users

app = Flask(__name__)
app.secret_key = config.secret_key

def require_login():
    if "user_id" not in session:
        abort(403)

@app.route("/")
def index():
    threads = forum.get_threads()
    return render_template("index.html", threads=threads)

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/search")
def search():
    query = request.args.get("query")
    results = forum.search(query) if query else []
    return render_template("search.html", query=query, results=results)

@app.route("/user/<int:id>")
def user(id):
    user = users.get_user(id)
    if not user:
        abort(404)
    messages = forum.get_user_messages(id)
    return render_template("user.html", user=user, messages=messages)

@app.route("/thread/<int:id>")
def show_thread(id):
    thread = forum.get_thread(id)
    if not thread:
        abort(404)
    messages = forum.get_messages(id)
    return render_template("thread.html", thread=thread, messages=messages)

@app.route("/new_thread", methods=["POST"])
def new_thread():
    require_login()

    title = request.form["title"]
    content = request.form["content"]
    if len(title) > 100 or len(content) > 5000:
        abort(403)
    user_id = session["user_id"]

    thread_id = forum.add_thread(title, content, user_id)
    return redirect("/thread/" + str(thread_id))

@app.route("/new_message", methods=["POST"])
def new_message():
    require_login()

    content = request.form["content"]
    if len(content) > 5000:
        abort(403)
    user_id = session["user_id"]
    thread_id = request.form["thread_id"]

    try:
        forum.add_message(content, user_id, thread_id)
    except:
        abort(403)
    return redirect("/thread/" + str(thread_id))

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_message(id):
    require_login()

    message = forum.get_message(id)
    if not message or message["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("edit.html", message=message)

    if request.method == "POST":
        content = request.form["content"]
        if len(content) > 5000:
            abort(403)
        forum.update_message(message["id"], content)
        return redirect("/thread/" + str(message["thread_id"]))

@app.route("/remove/<int:id>", methods=["GET", "POST"])
def remove_message(id):
    require_login()

    message = forum.get_message(id)
    if not message or message["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("remove.html", message=message)

    if request.method == "POST":
        if "continue" in request.form:
            forum.remove_message(message["id"])
        return redirect("/thread/" + str(message["thread_id"]))

@app.route("/new_user", methods=["POST"])
def new_user():
    username = request.form["username"]
    if len(username) > 16:
        abort(403)
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat"

    if users.create_user(username, password1):
        return "Tunnus luotu"
    else:
        return "VIRHE: tunnus on jo varattu"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    else:
        username = request.form["username"]
        password = request.form["password"]

        user_id = users.check_login(username, password)
        if user_id:
            session["user_id"] = user_id
            return redirect("/")
        else:
            return "VIRHE: väärä tunnus tai salasana"

@app.route("/logout")
def logout():
    require_login()

    del session["user_id"]
    return redirect("/")

@app.route("/add_image", methods=["GET", "POST"])
def add_image():
    require_login()

    if request.method == "GET":
        return render_template("add_image.html")

    if request.method == "POST":
        file = request.files["image"]
        if not file.filename.endswith(".jpg"):
            return "Väärä tiedostomuoto"

        image = file.read()
        if len(image) > 100 * 1024:
            return "Liian suuri kuva"

        user_id = session["user_id"]
        users.update_image(user_id, image)
        return redirect("/user/" + str(user_id))

@app.route("/image/<int:id>")
def show_image(id):
    image = users.get_image(id)
    if not image:
        abort(404)

    response = make_response(bytes(image))
    response.headers.set("Content-Type", "image/jpeg")
    return response