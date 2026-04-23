from flask import Flask

app=Flask(__name__)
@app.route("/")
def home():
    return "CreativePilot AI Backend Running"

app.run(debug=True)