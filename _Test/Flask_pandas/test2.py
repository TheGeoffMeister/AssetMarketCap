from flask import *
import pandas as pd
app = Flask(__name__)

@app.route("/tables")
def show_tables():
    data = pd.read_excel('dummy_data.xlsx')
    data.set_index(['Name'], inplace=True)
    data.index.name=None
    females = data.loc[data.Gender=='f']
    
    TABLES = [females.to_html(render_links=True,escape=False)]
    
    return render_template('view.html',tables=TABLES,
    titles = ['na', 'Female surfers'])

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)