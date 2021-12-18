from flask import Flask, render_template,jsonify

import numpy as np

app = Flask(__name__)

random_decimal = np.random.rand()

@app.route('/update_decimal', methods=['POST'])
def updatedecimal():
    random_decimal = np.random.rand()
    return jsonify('', render_template('random_decimal.html', x=random_decimal))


@app.route('/')
def index():
    return render_template('index.html', x=random_decimal)
        

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)

    