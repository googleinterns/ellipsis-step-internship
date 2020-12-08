""" demo app"""
from flask import Flask, request, render_template 
import os 

app = Flask(__name__)


@app.route('/')
def home_page():
    return render_template('index.html')


@app.route('/recognition')
def recognition_page():
    return render_template('recognition.html')


@app.route('/ingestion')
def ingestion_page():
    return render_template('ingestion.html')


@app.route('/result', methods=['POST'])
def submit_recognition():
    provider = request.form['provider']
    pipeline = request.form['pipeline_name']
    os.system('python3 ../../backend_jobs/recognition_pipeline/main.py  --region europe-west2  --input-ingestion-provider  FlickrProvider-2020 --input-recognition-provider Google_Vision_API --output gs://demo-bucket-step/results/outputs --runner DataflowRunner   --project step-project-ellispis   --temp_location gs://demo-bucket-step/tmp/ --requirements_file ../../requirements.txt --extra_package dist/pipeline-BACKEND_JOBS-0.0.1.tar.gz')
    return render_template('run.html', provider=provider, pipeline=pipeline)


@app.route('/result', methods=['POST'])
def submit_ingestion():
    provider = request.form['provider']
    pipeline = request.form['pipeline_name']
    os.system('python3 ../../backend_jobs/recognition_pipeline/main.py  --region europe-west2  --input-ingestion-provider  FlickrProvider-2020 --input-recognition-provider Google_Vision_API --output gs://demo-bucket-step/results/outputs --runner DataflowRunner   --project step-project-ellispis   --temp_location gs://demo-bucket-step/tmp/ --requirements_file ../../requirements.txt --extra_package dist/pipeline-BACKEND_JOBS-0.0.1.tar.gz')
    return render_template('run.html', provider=provider, pipeline=pipeline)


app.run()
