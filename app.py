from flask import Flask, flash
from flask import render_template, request, redirect, url_for
import os

import data
import constant_message as msg
import postgresdb as db
from models import Vacancy, Event, User, Document, Template, EmailCredential
from email_lib import EmailWrapper
from mongodb import MongoDatabase
from celery_worker import async_send_mail


app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    """
    Show homepage
    Returns:
        Homepage greeting
    """
    return render_template('home.html', title='Vacancies CRM')


@app.route('/vacancies', methods=['GET', 'POST'])
@app.route('/vacancies/', methods=['GET', 'POST'])
def vacancies():
    """
    Get all vacancies and post new vacancy function
    Returns:
        list - list of dictionaries of vacancies
    """
    if not db.init_db():
        flash(msg.CONNECTION_ERR, category="danger")
    if request.method == 'POST':
        if request.form.get('position_name', '').strip() == '':
            flash(msg.POPULATION_ERR.format(field='Position name'), category='danger')
            return redirect(url_for('vacancies'))
        if request.form.get('company', '').strip() == '':
            flash(msg.POPULATION_ERR.format(field='Company'), category='danger')
            return redirect(url_for('vacancies'))
        if request.form.get('description', '').strip() == '':
            flash(msg.POPULATION_ERR.format(field='Description'), category='danger')
            return redirect(url_for('vacancies'))

        contact_name = request.form.get('contact_name')
        contact_email = request.form.get('contact_email')
        contact_phone = request.form.get('contact_phone')
        new_contact_id = 0
        try:
            contact = MongoDatabase('contacts_db', 'contacts')
            new_contact_id = contact.insert_record(name=contact_name,
                                            email=contact_email,
                                            phone=contact_phone)
        except Exception as err:
            print(err)

        position_name = request.form.get('position_name')
        company = request.form.get('company')
        description = request.form.get('description')
        comment = request.form.get('comment')
        url = request.form.get('url')

        vacancy_data = Vacancy(position_name=position_name,
                               company=company,
                               description=description,
                               contacts_ids=str(new_contact_id),
                               comment=comment,
                               url=url,
                               status=1,
                               user_id=1
                               )
        try:
            db.db_session.add(vacancy_data)
            db.db_session.commit()
        except Exception as err:
            print(f'Vacancy adding error:\n{err}')

    all_vacancies = db.db_session.query(Vacancy).order_by(-Vacancy.id).all()
    return render_template('vacancies.html',
                           title='All vacancies',
                           vacancies=all_vacancies)


@app.route('/vacancy/<int:vacancy_id>', methods=['GET', 'POST'])
@app.route('/vacancy/<int:vacancy_id>/', methods=['GET', 'POST'])
def vacancy(vacancy_id):
    """
    Show/Edit specific vacancy by ID
    Args:
        vacancy_id: int - id of specific vacancy
    Returns:
        dict - data of specific vacancy
    """
    if not db.init_db():
        flash(msg.CONNECTION_ERR, category="danger")

    contact = MongoDatabase('contacts_db', 'contacts')

    if request.method == 'POST':
        if request.form.get('position_name', '').strip() == '':
            flash(msg.POPULATION_ERR.format(field='Position name'), category='danger')
            return redirect(url_for('vacancies'))
        if request.form.get('company', '').strip() == '':
            flash(msg.POPULATION_ERR.format(field='Company'), category='danger')
            return redirect(url_for('vacancies'))
        if request.form.get('description', '').strip() == '':
            flash(msg.POPULATION_ERR.format(field='Description'), category='danger')
            return redirect(url_for('vacancies'))

        contact_name = request.form.get('contact_name')
        contact_email = request.form.get('contact_email')
        contact_phone = request.form.get('contact_phone')
        contact_id = request.form.get('_id')

        new_contact_id = contact.insert_record(name=contact_name,
                                            email=contact_email,
                                            phone=contact_phone)

        position_name = request.form.get('position_name')
        company = request.form.get('company')
        description = request.form.get('description')
        comment = request.form.get('comment')
        url = request.form.get('url')
        status = request.form.get('status')

        contact_ids = ''
        if new_contact_id:
            contact_ids = ',' + str(new_contact_id)

        try:
            vacancy_to_upd = db.db_session.query(Vacancy).get(vacancy_id)
            vacancy_to_upd.position_name = position_name
            vacancy_to_upd.company = company
            vacancy_to_upd.description = description
            vacancy_to_upd.contacts_ids = vacancy_to_upd.contacts_ids + contact_ids
            vacancy_to_upd.comment = comment
            vacancy_to_upd.url = url
            vacancy_to_upd.status = status
            db.db_session.commit()
            # if vacancy_to_upd.contacts_ids:
            #     contacts_to_upt = vacancy_to_upd.contacts_ids.split(',')
            #     contact.update_record(contacts_to_upt)
            print('vacancy_to_upd.contacts_ids = ', vacancy_to_upd.contacts_ids)
            print('type: ',type(vacancy_to_upd.contacts_ids))
        except Exception as err:
            print(f'Vacancy updating error:\n{err}')

    mail = EmailWrapper(login='volodymyr.di@gmail.com', password=os.environ.get('EMAIL_PASSWORD'),
                        pop_server='pop.gmail.com', pop_port=995,
                        imap_server='imap.gmail.com', imap_port=993,
                        smtp_server='smtp.gmail.com', smtp_port=465)
    specific_vacancy = db.db_session.query(Vacancy).filter_by(id=vacancy_id).first()
    contact_ids = str(specific_vacancy.contacts_ids).split(',')
    vacancy_contacts = contact.select(contact_ids)
    emails = dict(reversed(list(mail.get_mail_by_pop().items())))
    return render_template('vacancy.html',
                           title=specific_vacancy.position_name,
                           specific_vacancy=specific_vacancy,
                           vacancy_contacts=vacancy_contacts,
                           emails=emails)


@app.route('/vacancy/<int:vacancy_id>/contact/<string:_id>', methods=['GET', 'POST'])
@app.route('/vacancy/<int:vacancy_id>/contact/<string:_id>/', methods=['GET', 'POST'])
def contact_update(vacancy_id, _id):
    if request.method == 'POST':
        contact = MongoDatabase('contacts_db', 'contacts')
        contact.update_record(_id, new_data=request.form.items())
    return redirect(url_for('vacancy', vacancy_id=vacancy_id))


@app.route('/vacancy/<int:vacancy_id>/events', methods=['GET', 'POST'])
@app.route('/vacancy/<int:vacancy_id>/events/', methods=['GET', 'POST'])
def vacancy_events(vacancy_id):
    """
    Show/Edit all vacancy's events
    Args:
        vacancy_id: int - ID of specific vacancy
    Returns:
        list - list of events
    """
    if not db.init_db():
        flash(msg.CONNECTION_ERR, category="danger")
    if request.method == 'POST':
        if request.form.get('title', '').strip() == '':
            flash(msg.POPULATION_ERR.format(field='Title'), category='danger')
            return redirect(url_for('vacancy_events'))

        title = request.form.get('title')
        description = request.form.get('description')
        due_to_date = request.form.get('due_to_date')

        new_event = Event(vacancy_id=vacancy_id,
                          title=title,
                          description=description,
                          due_to_date=due_to_date,
                          status=1
                          )
        try:
            db.db_session.add(new_event)
            db.db_session.commit()
        except Exception as err:
            print(f'Event adding error:\n{err}')

    vacancy_name = db.db_session.query(Vacancy).filter_by(id=vacancy_id).first().position_name
    events = db.db_session.query(Event).filter_by(vacancy_id=vacancy_id).order_by(-Event.id).all()

    return render_template('events.html',
                           vacancy_id=vacancy_id,
                           title=vacancy_name,
                           events=events)


@app.route('/vacancy/<int:vacancy_id>/event/<int:event_id>', methods=['GET', 'POST'])
def vacancy_event(vacancy_id, event_id):
    """
    Show/Edit specific event of specific vacancy
    Args:
        vacancy_id: int
        event_id: int
    Returns:
        dict - dictionary of event's data
    """
    if not db.init_db():
        flash(msg.CONNECTION_ERR, category="danger")
    if request.method == 'POST':
        if request.form.get('title', '').strip() == '':
            flash(msg.POPULATION_ERR.format(field='Title'), category='danger')
            return redirect(url_for('vacancy_event'))

        if request.form.get('status', '').strip() == '':
            flash(msg.POPULATION_ERR.format(field='Status'), category='danger')
            return redirect(url_for('vacancy_event'))

        title = request.form.get('title')
        description = request.form.get('description')
        due_to_date = request.form.get('due_to_date')
        status = request.form.get('status')

        try:
            event_to_upd = db.db_session.query(Event).filter_by(id=event_id, vacancy_id=vacancy_id).first()
            event_to_upd.title = title
            event_to_upd.description = description
            event_to_upd.due_to_date = due_to_date
            event_to_upd.status = status
            db.db_session.commit()
        except Exception as err:
            print(f'Event updating error:\n{err}')

    specific_event = db.db_session.query(Event).filter_by(id=event_id, vacancy_id=vacancy_id).first()

    return render_template('event.html',
                           specific_event=specific_event)


@app.route('/vacancy/<int:vacancy_id>/history', methods=['GET'])
def vacancy_history(vacancy_id):
    """
    Get vacancy's history
    Args:
        vacancy_id: int - specific vacancy's ID
    Returns:
        list - list of vacancy's history dictionaries
    """
    history = data.History(vacancy_id).get_history
    return render_template('history.html',
                           title=f'History of vacancy {vacancy_id}',
                           history=history)


@app.route('/user', methods=['GET'])
def user_menu():
    """
    Get user's data
    Returns:
        list - list of user's data dictionary
    """
    if not db.init_db():
        flash(msg.CONNECTION_ERR, category="danger")
    user_data = ''
    documents = ''
    templates = ''
    email_cred = ''

    try:
        user_data = db.db_session.query(User).first()
        documents = db.db_session.query(Document).all()
        templates = db.db_session.query(Template).all()
        email_cred = db.db_session.query(EmailCredential).first()
    except Exception as err:
        print(f'User data loading error:\n{err}')

    return render_template('user.html',
                           title='User menu',
                           user_data=user_data,
                           documents=documents,
                           templates=templates,
                           email_cred=email_cred)


@app.route('/user/calendar', methods=['GET'])
def user_calendar():
    return 'User calendar'


@app.route('/user/mail', methods=['GET', 'POST'])
def user_mail():
    """
    Send mail to recipient
    Returns: redirection to page of 'vacancies'
    """
    if not db.init_db():
        flash(msg.CONNECTION_ERR, category="danger")
    if request.method == 'POST':
        if request.form.get('recipient', '').strip() == '':
            flash(msg.POPULATION_ERR.format(field='Recipient'), category='danger')
            return redirect(url_for('send_mail'))

        if request.form.get('subject', '').strip() == '':
            flash(msg.POPULATION_ERR.format(field='Subject'), category='danger')
            return redirect(url_for('send_mail'))

        recipient = request.form.get('recipient')
        subject = request.form.get('subject')
        message = request.form.get('message')
        creds_id = db.db_session.query(EmailCredential).filter_by(user_id=1).first()

        async_send_mail.apply_async(args=[creds_id.id, recipient, subject, message])
        return redirect(url_for('vacancies'))

    return render_template('send-mail.html', title='Send mail')


@app.route('/user/settings', methods=['GET', 'POST'])
def user_settings():
    """
    Edit user data
    Returns:
        tuples - User, Document, Template data
    """
    if not db.init_db():
        flash(msg.CONNECTION_ERR, category="danger")
    if request.method == 'POST':
        if request.form.get('user_name', '').strip() == '':
            flash(msg.POPULATION_ERR.format(field='Name'), category='danger')
            return redirect(url_for('user_settings'))

        if request.form.get('login', '').strip() == '':
            flash(msg.POPULATION_ERR.format(field='Login'), category='danger')
            return redirect(url_for('user_settings'))

        if request.form.get('passwd', '').strip() == '':
            flash(msg.POPULATION_ERR.format(field='Password'), category='danger')
            return redirect(url_for('user_settings'))

        if request.form.get('email', '').strip() == '':
            flash(msg.POPULATION_ERR.format(field='Email'), category='danger')
            return redirect(url_for('user_settings'))

        user_name = request.form.get('user_name')
        login = request.form.get('login')
        passwd = request.form.get('passwd')
        email = request.form.get('email')

        if request.form.get('email_login', '').strip() == '':
            flash(msg.POPULATION_ERR.format(field='Email Login'), category='danger')
            return redirect(url_for('user_settings'))

        if request.form.get('email_passwd', '').strip() == '':
            flash(msg.POPULATION_ERR.format(field='Email Password'), category='danger')
            return redirect(url_for('user_settings'))

        if request.form.get('pop_server', '').strip() == '':
            flash(msg.POPULATION_ERR.format(field='POP-server'), category='danger')
            return redirect(url_for('user_settings'))

        if request.form.get('smtp_server', '').strip() == '':
            flash(msg.POPULATION_ERR.format(field='SMTP-server'), category='danger')
            return redirect(url_for('user_settings'))

        email_login = request.form.get('email_login')
        email_passwd = request.form.get('email_passwd')
        pop_server = request.form.get('pop_server')
        smtp_server = request.form.get('smtp_server')

        try:
            user_to_upd = db.db_session.query(User).first()
            if user_to_upd:
                user_to_upd.name = user_name
                user_to_upd.login = login
                user_to_upd.passwd = passwd
                user_to_upd.email = email
            else:
                new_user = User(name=user_name,
                                login=login,
                                password=passwd,
                                email=email)
                db.db_session.add(new_user)
                db.db_session.commit()
            email_cred_to_upd = db.db_session.query(EmailCredential).first()
            if email_cred_to_upd:
                email_cred_to_upd.email_login = email_login
                email_cred_to_upd.email_passwd = email_passwd
                email_cred_to_upd.pop_server = pop_server
                email_cred_to_upd.smtp_server = smtp_server
                email_cred_to_upd.user_id = 1
            else:
                new_email_cred = EmailCredential(email_login=email_login,
                                                 email_passwd=email_passwd,
                                                 pop_server=pop_server,
                                                 smtp_server=smtp_server,
                                                 user_id=1)
                db.db_session.add(new_email_cred)
                db.db_session.commit()
            return redirect(url_for('user_menu'))
        except Exception as err:
            print(err)

    user_data = db.db_session.query(User).first()
    email_cred = db.db_session.query(EmailCredential).first()
    documents = db.db_session.query(Document).all()
    templates = db.db_session.query(Template).all()
    return render_template('user-settings.html',
                           title='User menu',
                           user_data=user_data,
                           documents=documents,
                           templates=templates,
                           email_cred=email_cred)


@app.route('/user/documents', methods=['GET', 'POST'])
def user_documents():
    return data.documents


@app.route('/user/templates', methods=['GET', 'POST'])
def user_templates():
    return 'User templates'


@app.route('/vacancy/<int:vacancy_id>/contacts', methods=['GET', 'POST'])
def add_contact(vacancy_id):
    if request.method == 'POST':
        name = request.form.get('name')
        mail = request.form.get('email')
        phone = request.form.get('phone')

        print(name, mail, phone)
    return redirect(url_for('vacancy', vacancy_id=vacancy_id))


@app.route('/vacancy/<int:vacancy_id>/contact/<string:contact_id>', methods=['GET', 'POST'])
def edit_contact(vacancy_id, contact_id):
    if request.method == 'POST':
        if contact_id:
            for _ in request.form.get('contact_id'):
                name = request.form.get('name')
                mail = request.form.get('email')
                phone = request.form.get('phone')
                print(name, mail, phone)
    return redirect(url_for('vacancy', vacancy_id=vacancy_id))


if __name__ == '__main__':
    app.secret_key = '!@JkikSPdkp9871jiod89^%&*&Ghuhgu'
    app.run(debug=True, use_reloader=True, host="0.0.0.0", port=5050)
