from celery import Celery
from email_lib import EmailWrapper
from models import EmailCredential
import postgresdb as db
import os


WORKING_HOST = os.environ.get('RABBIT_HOST', 'localhost')
app = Celery('celery_worker', broker=f'pyamqp://guest@{WORKING_HOST}//')


@app.task
def async_send_mail(cred_id, recipient, subject, message):
    db.init_db()
    email_creds = db.db_session.query(EmailCredential).get(cred_id)
    email_wrapper = EmailWrapper(**email_creds.get_smtp_mandatory_fields())
    email_wrapper.send_mail(recipient, subject, message)
