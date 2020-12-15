from backend_jobs.pipeline_utils.firestore_database import initialize_db
from backend_jobs.pipeline_utils import database_schema
from firebase_admin import firestore

_NUM_OF_LATEST_RUNS = 10

def get_latest_runs(status):
    db = initialize_db()
    query = db.collection(database_schema.COLLECTION_PIPELINE_RUNS).where(\
        database_schema.COLLECTION_PIPELINE_RUNS_FIELD_STATUS, u'==', status).\
            order_by(database_schema.COLLECTION_PIPELINE_RUNS_FIELD_START_DATE, direction=firestore.Query.DESCENDING).\
                limit(_NUM_OF_LATEST_RUNS).stream()
    return [doc.to_dict() for doc in query]


print(get_latest_runs('FAILED'))
    
    