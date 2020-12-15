""" demo app"""
from flask import request, render_template 
from backend_jobs.recognition_pipeline.main import run
from flask import Flask
from flask_celery import make_celery


app = Flask(__name__)
app.config.update(
    CELERY_BROKER_URL='amqp://guest:guest@localhost:5672//',
)
celery = make_celery(app)


INPUT_TYPE_PROVIDER = 'provider'
INPUT_TYPE_RUN_ID = 'run-id'
TEST_OUTPUT = 'outputs'


@celery.task(name='run_task')
def create_recognition_task(input_type, input_value, input_recognition_provider):
    if input_type == INPUT_TYPE_PROVIDER:
        run(recognition_provider_name=input_recognition_provider, ingestion_provider=input_value, output_name=TEST_OUTPUT, run_locally=True)
    else:
        run(recognition_provider_name=input_recognition_provider, ingestion_run=input_value, output_name=TEST_OUTPUT, run_locally=True)
    return 'hi'
'''
    if input_type == INPUT_TYPE_PROVIDER:
            thread = Thread(target=run, kwargs={
            'recognition_provider_name': input_recognition_provider, 'ingestion_provider': input_value, 'output_name': TEST_OUTPUT, 'run_locally': True})
        thread.start()
    else:
        thread = Thread(target=run, kwargs={
            'recognition_provider_name': input_recognition_provider, 'ingestion_run': input_value, 'output_name': TEST_OUTPUT, 'run_locally': True})
        thread.start()
'''

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


@app.route('/', methods=['POST'])
def submit_recognition():
    input_type = request.form['input_type']
    input_value = request.form['input_value']
    input_recognition_provider = request.form['recognition_provider']
    task = create_recognition_task.delay(input_type, input_value, input_recognition_provider)
    print(task)
    return render_template('index.html')


@app.route('/result', methods=['POST'])
def submit_ingestion():
    provider = request.form['provider']
    pipeline = request.form['pipeline_name']
    #os.system('python3 ../../backend_jobs/recognition_pipeline/main.py  --region europe-west2  --input-ingestion-provider  FlickrProvider-2020 --input-recognition-provider Google_Vision_API --output gs://demo-bucket-step/results/outputs --runner DataflowRunner   --project step-project-ellispis   --temp_location gs://demo-bucket-step/tmp/ --requirements_file ../../requirements.txt --extra_package dist/pipeline-BACKEND_JOBS-0.0.1.tar.gz')
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


if __name__=='__main__':
    app.run(debug=True)
