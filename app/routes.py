from datetime import datetime

from flask import render_template

from app import app


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/zip/<zip>')
def zip(zip):
    return render_template("zip.html", zip=zip, time=datetime.now())


# @app.route('/hello')
# def hello():
# app.logger.debug('A value for debugging')
#     app.logger.warning('A warning occurred (%d apples)', 42)
#     app.logger.error('An error occurred')
#     return 'And hello to you!'
