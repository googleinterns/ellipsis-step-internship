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


@app.route('/ingestion_')
def ingestion_page():
    return render_template('ingestion.html')


@app.route('/ingestion_verification')
def ingestion_verification_page():
    return render_template('ingestion_verification.html')


@app.route('/recognition_verification')
def recognition_verification_page():
    return render_template('recognition_verification.html')


@app.route('/ingestion_removal')
def ingestion_removal_page():
    return render_template('ingestion_removal.html')


@app.route('/recognition_removal')
def recognition_removal_page():
    return render_template('recognition_removal.html')


@app.route('/result', methods=['POST'])
def submit_recognition():
    input_type = request.form['input_type']
    input_value = request.form['input_value']
    #os.system('python3 ../../backend_jobs/recognition_pipeline/main.py  --region europe-west2  --input-ingestion-provider  FlickrProvider-2020 --input-recognition-provider Google_Vision_API --output gs://demo-bucket-step/results/outputs --runner DataflowRunner   --project step-project-ellispis   --temp_location gs://demo-bucket-step/tmp/ --requirements_file ../../requirements.txt --extra_package dist/pipeline-BACKEND_JOBS-0.0.1.tar.gz')
    return render_template('run.html', input_type=input_type, input_value=input_value)


@app.route('/result', methods=['POST'])
def submit_ingestion():
    provider = request.form['provider']
    pipeline = request.form['pipeline_name']
    os.system('python3 ../../backend_jobs/recognition_pipeline/main.py  --region europe-west2  --input-ingestion-provider  FlickrProvider-2020 --input-recognition-provider Google_Vision_API --output gs://demo-bucket-step/results/outputs --runner DataflowRunner   --project step-project-ellispis   --temp_location gs://demo-bucket-step/tmp/ --requirements_file ../../requirements.txt --extra_package dist/pipeline-BACKEND_JOBS-0.0.1.tar.gz')
    return render_template('run.html', provider=provider, pipeline=pipeline)

@app.route('/result', methods=['POST'])
def submit_recognition_removal():
    pass


app.run()
