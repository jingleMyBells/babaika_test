from flask import render_template

from . import app


@app.route('/list', methods=['GET'])
def index_view():
    return render_template('list.html')