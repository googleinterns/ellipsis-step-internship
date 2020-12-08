""" demo app"""
from flask import Flask, request, render_template

app = Flask(__name__)


@app.route('/')
def home_page():
    example_embed = 'This string is from python'
    return render_template('index.html', embed=example_embed)


@app.route('/result', methods=['POST'])
def submit():
    provider = request.form['provider']
    pipeline = request.form['pipeline_name']
    print("The provider ", provider)
    print("The pipeline ", pipeline)
    return render_template('run.html', provider=provider, pipeline=pipeline)


app.run()
