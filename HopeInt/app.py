from flask import Flask, render_template, request, redirect
import os

app = Flask(__name__, template_folder='frontend')

# Dummy login logic (replace with DB or CSV logic as needed)
users = {
    "donor@example.com": "donor123",
    "orphanage@example.com": "orphan123",
    "volunteer@example.com": "volunteer123"
}

@app.route("/")
@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login_post():
    email = request.form.get("email")
    password = request.form.get("password")

    if email in users and users[email] == password:
        # Redirect to Streamlit chatbot
        return redirect("http://localhost:8501")
    else:
        return "Invalid credentials", 401

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/home")
def home():
    return render_template("hopehaven.html")

if __name__ == "__main__":
    app.run(debug=True)
