from datetime import datetime
from flask import Flask, render_template

app = Flask(__name__)

REFERENCE_ADDRESS = "Rua Aristides Crivellaro, 228 - Macuco, Valinhos - SP, 13279-813"

@app.get("/")
def index():
    return render_template("index.html", reference_address=REFERENCE_ADDRESS)

@app.get("/privacidade")
def privacy():
    return render_template("privacy.html")

@app.get("/termos")
def terms():
    return render_template("terms.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
