# -*- coding: utf-8 -*-
"""
Created on Fri May 28 22:02:01 2021

@author: Geoff
"""


from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

if __name__ == "__main__":
    app.run()