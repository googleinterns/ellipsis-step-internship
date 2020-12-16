""" demo app"""
from threading import Thread
from flask import Flask, request, render_template
from firebase_admin import firestore
from backend_jobs.recognition_pipeline.main import run as run_recognition_pipeline
from backend_jobs.ingestion_pipeline.main import run as run_ingestion_pipeline
from backend_jobs.pipeline_utils.firestore_database import initialize_db
from backend_jobs.pipeline_utils import database_schema


app = Flask(__name__)

INPUT_TYPE_PROVIDER = 'provider'
INPUT_TYPE_RUN_ID = 'run-id'
TEST_OUTPUT = 'outputs'
_NUM_OF_LATEST_RUNS = 10


def get_latest_runs(status):
    db = initialize_db()
    query = db.collection(database_schema.COLLECTION_PIPELINE_RUNS)\
        .where(database_schema.COLLECTION_PIPELINE_RUNS_FIELD_STATUS, u'==', status)\
        .order_by(database_schema.COLLECTION_PIPELINE_RUNS_FIELD_START_DATE, direction=firestore.Query.DESCENDING)\
        .limit(_NUM_OF_LATEST_RUNS).stream()
    return [doc.to_dict() for doc in query]


@app.route('/')
def home_page():
    return render_template('index.html')


@app.route('/all_pipelines', methods=['GET'])
def all_pipelines_page():
    return render_template('all_pipelines.html')


@app.route('/submit_all_pipeline', methods=['POST'])
def submit_all_pipelines_page():
    status_type = request.form['status_type']
    my_objects = get_latest_runs(status_type)
    return render_template('all_pipelines.html', my_objects=my_objects)


@app.route('/recognition')
def recognition_page():
    return render_template('recognition.html')


@app.route('/ingestion')
def ingestion_page():
    return render_template('ingestion.html')


@app.route('/submit_recognition', methods=['POST'])
def submit_recognition():
    input_type = request.form['input_type']
    input_value = request.form['input_value']
    input_recognition_provider = request.form['recognition_provider']
    if input_type == INPUT_TYPE_PROVIDER:
        thread = Thread(target=run_recognition_pipeline, kwargs={
            'recognition_provider_name': input_recognition_provider,
            'ingestion_provider': input_value,
            'output_name': TEST_OUTPUT,
            'run_locally': True})
        thread.start()
    else:
        thread = Thread(target=run_recognition_pipeline, kwargs={
            'recognition_provider_name': input_recognition_provider,
            'ingestion_run': input_value,
            'output_name': TEST_OUTPUT,
            'run_locally': True})
        thread.start()
    return render_template('index.html')


@app.route('/submit_ingestion', methods=['POST'])
def submit_ingestion():
    input_value = request.form['input_value']
    print(input_value)
    input_provider_args = request.form['arguments']
    print(input_provider_args)
    thread = Thread(target=run_ingestion_pipeline, kwargs={
        'input_provider_name': input_value,
        'input_provider_args': input_provider_args,
        'output_name': TEST_OUTPUT,
        'run_locally': True})
    thread.start()
    return render_template('index.html')


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
def submit_recognition_verification():
    pass


@app.route('/result', methods=['POST'])
def submit_ingestion_verification():
    pass


@app.route('/result', methods=['POST'])
def submit_recognition_removal():
    pass


@app.route('/result', methods=['POST'])
def submit_ingestion_removal():
    pass


if __name__ == '__main__':
    app.run(debug=True)
