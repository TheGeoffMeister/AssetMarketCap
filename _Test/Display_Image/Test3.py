from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    full_filename = 'https://logo.clearbit.com/3m.com'
    return render_template("index.html", user_image = full_filename)
        

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)

    