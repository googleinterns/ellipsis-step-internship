""" demo app"""
from flask import Flask, request, render_template 
from backend_jobs.recognition_pipeline.main import run
from celery import Celery

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

app = Flask(__name__)
client = Celery(app.name, broker='pyamqp://guest@localhost//')





BUCKET='demo-bucket-step'
REGION='europe-west2'
PROJECT='step-project-ellispis'
INPUT_TYPE_PROVIDER = 'provider'
INPUT_TYPE_RUN_ID = 'run-id'
TEST_OUTPUT = 'outputs'


@client.task
def create_recognition_task(input_type, input_value, input_recognition_provider):
    if input_type == INPUT_TYPE_PROVIDER:
        run(recognition_provider_name=input_recognition_provider, ingestion_provider=input_value, output_name=TEST_OUTPUT, run_locally=True)
    else:
        run(recognition_provider_name=input_recognition_provider, ingestion_run=input_value, output_name=TEST_OUTPUT, run_locally=True)
    '''
    if input_type == INPUT_TYPE_PROVIDER:
            thread = Thread(target=run, kwargs={
            'recognition_provider_name': input_recognition_provider, 'ingestion_provider': input_value, 'output_name': TEST_OUTPUT, 'run_locally': True})
        thread.start()
    else:
        thread = Thread(target=run, kwargs={
            'recognition_provider_name': input_recognition_provider, 'ingestion_run': input_value, 'output_name': TEST_OUTPUT, 'run_locally': True})
        thread.start()'''


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


@app.route('/', methods=['POST', 'GET'])
def submit_recognition():
    input_type = request.form['input_type']
    input_value = request.form['input_value']
    input_recognition_provider = request.form['recognition_provider']
    task = create_recognition_task.delay(input_type, input_value, input_recognition_provider)
    return render_template('index.html')


@app.route('/result', methods=['POST'])
def submit_ingestion():
    provider = request.form['provider']
    pipeline = request.form['pipeline_name']
    os.system('python3 ../../backend_jobs/recognition_pipeline/main.py  --region europe-west2  --input-ingestion-provider  FlickrProvider-2020 --input-recognition-provider Google_Vision_API --output gs://demo-bucket-step/results/outputs --runner DataflowRunner   --project step-project-ellispis   --temp_location gs://demo-bucket-step/tmp/ --requirements_file ../../requirements.txt --extra_package dist/pipeline-BACKEND_JOBS-0.0.1.tar.gz')
    return render_template('run.html', provider=provider, pipeline=pipeline)

@app.route('/result', methods=['POST'])
def submit_recognition_verification():
    pass

@app.route('/result', methods=['POST'])
def submit_ingestion_verification():
    pass

@app.route('/result', methods=['POST'])
def submit_recognition_removal():
    input_type = request.form['input_type']
    input_value = request.form['input_value']

@app.route('/result', methods=['POST'])
def submit_ingestion_removal():
    pass



app.run()
