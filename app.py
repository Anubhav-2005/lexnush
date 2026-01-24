from flask import Flask, render_template

app = Flask(__name__)

# Home stays the same (it naturally becomes index.html)
@app.route("/")
def home():
    return render_template("index.html")

# ADD A SLASH '/' TO THE END OF ALL THESE ROUTES:

@app.route("/about/") 
def about():
    return render_template("about.html")

@app.route("/blogs/")
def blogs():
    return render_template("blogs.html")

@app.route("/interviews/")
def interviews():
    return render_template("interviews.html")

@app.route("/contact/")
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug=True)