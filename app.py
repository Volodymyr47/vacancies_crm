from flask import Flask, flash
from flask import render_template, request, redirect, url_for
from flask import session
from flask import Response

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
    current_user = session.get('user_name', None)
    return render_template('home.html', title='Vacancies CRM', username = current_user)


@app.route('/login', methods=['GET', 'POST'])
@app.route('/login/', methods=['GET', 'POST'])
def login():
    """
    User login function
    Returns: redirection to home-page if having login success or login-page if received login-error
    """
    if request.method == 'POST':
        user_login = request.form.get('user_login').lower()
        user_password = request.form.get('password')
        if user_login.strip() in ['', None] or user_password.strip() in ['', None]:
            flash(msg.POPULATION_ERR.format(field='Login or Password'), category='warning')
            return redirect(url_for('login'))
        user = db.db_session.query(User).filter_by(login=user_login).first()
        if user is None:
            flash(msg.LOGIN_ERR, category='warning')
            return redirect(url_for('login'))
        if user_password != user.passwd:
            flash(msg.LOGIN_ERR, category='warning')
            return redirect(url_for('login'))
        session['user_id'] = user.id
        session['user_name'] = user.name
        return redirect(url_for('home'))
    return render_template('login.html', title='Login')


@app.route('/logout')
@app.route('/logout/')
def logout():
    """
    User-logout function
    Returns: redirection to home-page
    """
    if not session.get('user_id'):
        return redirect(url_for('login'))
    session.pop('user_id')
    session.pop('user_name')
    return redirect(url_for('home'))


@app.route('/registration', methods=['GET', 'POST'])
@app.route('/registration/', methods=['GET', 'POST'])
def registration():
    """
    User-registration function
    Returns: redirection to home-page if having registration success
    or registration-page if received login-error

    """
    if session.get('user_id'):
        return redirect(url_for('home'))
    if request.method == 'POST':
        user_login = request.form.get('user_login').lower()
        user_password = request.form.get('password')
        conf_password = request.form.get('conf_password')
        full_name = request.form.get('fullname')
        user_email = request.form.get('email')

        if user_password != conf_password:
            flash(msg.PASSWORD_MATCH_ERR, category='warning')
            return redirect(url_for('registration'))

        user = db.db_session.query(User).filter_by(login=user_login).first()
        if user:
            flash(msg.USERNAME_ERR, category='warning')
            return redirect(url_for('registration'))
        try:
            new_user = User(login=user_login, password=user_password,
                            name=full_name, email=user_email)
            db.db_session.add(new_user)
            db.db_session.commit()
            return redirect(url_for('login'))
        except Exception as err:
            flash(msg.REGISTRATION_ERR, category='danger')
            print(f'Registration error:\n{err}')
            return redirect(url_for('home'))
    return render_template('registration.html', title='Registration')


@app.route('/vacancies', methods=['GET', 'POST'])
@app.route('/vacancies/', methods=['GET', 'POST'])
def vacancies():
    """
    Get all vacancies and post new vacancy function
    Returns:
        list - list of dictionaries of vacancies
    """
    if not session.get('user_id'):
        return redirect(url_for('login'))
    user_id = session.get('user_id')

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
                               user_id=user_id
                               )
        try:
            db.db_session.add(vacancy_data)
            db.db_session.commit()
        except Exception as err:
            print(f'Vacancy adding error:\n{err}')

    all_vacancies = db.db_session.query(Vacancy).filter_by(user_id=user_id).order_by(-Vacancy.id).all()
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
    if not session.get('user_id'):
        return redirect(url_for('login'))
    user_id = session.get('user_id')

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
            vacancy_to_upd = db.db_session.query(Vacancy).filter_by(user_id=user_id).get(vacancy_id)
            vacancy_to_upd.position_name = position_name
            vacancy_to_upd.company = company
            vacancy_to_upd.description = description
            vacancy_to_upd.contacts_ids = vacancy_to_upd.contacts_ids + contact_ids
            vacancy_to_upd.comment = comment
            vacancy_to_upd.url = url
            vacancy_to_upd.status = status
            db.db_session.commit()
        except Exception as err:
            print(f'Vacancy updating error:\n{err}')

    user_cred = db.db_session.query(EmailCredential).filter_by(user_id=user_id).first()
    mail = EmailWrapper(**user_cred.get_pop_mandatory_fields())
    specific_vacancy = db.db_session.query(Vacancy).\
        filter_by(id=vacancy_id).\
        filter_by(user_id=user_id).first()

    if not specific_vacancy:
        return Response(status=404)

    contact_ids = str(specific_vacancy.contacts_ids).split(',')
    vacancy_contacts = contact.select(contact_ids)
    emails = dict(reversed(list(mail.get_mail_by_pop().items())))
    return render_template('vacancy.html',
                           title=specific_vacancy.position_name,
                           specific_vacancy=specific_vacancy,
                           vacancy_contacts=vacancy_contacts,
                           emails=emails)


@app.route('/vacancy/<int:vacancy_id>/contact/<string:_id>', methods=['POST'])
@app.route('/vacancy/<int:vacancy_id>/contact/<string:_id>/', methods=['POST'])
def contact_update(vacancy_id, _id):
    """
    Update existing contact
    Args:
        vacancy_id: int
        _id: string

    Returns: redirect to vacancy form
    """
    if not session.get('user_id'):
        return redirect(url_for('login'))

    updated_data = request.form.items()
    try:
        updated_data = dict(updated_data)
    except Exception as err:
        print(err)

    contact = MongoDatabase('contacts_db', 'contacts')
    contact.update_record(_id, new_data=updated_data)
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
    if not session.get('user_id'):
        return redirect(url_for('login'))
    user_id = session.get('user_id')

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

    vacancy_name = db.db_session.query(Vacancy).\
        filter_by(id=vacancy_id).\
        filter_by(user_id=user_id).first().position_name
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
    if not session.get('user_id'):
        return redirect(url_for('login'))

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
    if not session.get('user_id'):
        return redirect(url_for('login'))

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
    if not session.get('user_id'):
        return redirect(url_for('login'))
    user_id = session.get('user_id')

    if not db.init_db():
        flash(msg.CONNECTION_ERR, category="danger")
    user_data = ''
    documents = ''
    templates = ''
    email_cred = ''

    try:
        user_data = db.db_session.query(User).filter_by(id=user_id).first()
        documents = db.db_session.query(Document).all()
        templates = db.db_session.query(Template).filter_by(user_id=user_id).all()
        email_cred = db.db_session.query(EmailCredential).filter_by(user_id=user_id).first()
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
    if not session.get('user_id'):
        return redirect(url_for('login'))
    user_id = session.get('user_id')

    return 'User calendar'


@app.route('/user/mail', methods=['GET', 'POST'])
def user_mail():
    """
    Send mail to recipient
    Returns: redirection to page of 'vacancies'
    """
    if not session.get('user_id'):
        return redirect(url_for('login'))
    user_id = session.get('user_id')

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
        creds_id = db.db_session.query(EmailCredential).filter_by(user_id=user_id).first()

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
    if not session.get('user_id'):
        return redirect(url_for('login'))
    user_id = session.get('user_id')

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
        user_login = request.form.get('login')
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
            user_to_upd = db.db_session.query(User).filter_by(id=user_id).first()
            if user_to_upd:
                user_to_upd.name = user_name
                user_to_upd.login = user_login
                user_to_upd.passwd = passwd
                user_to_upd.email = email
            else:
                new_user = User(name=user_name,
                                login=user_login,
                                password=passwd,
                                email=email)
                db.db_session.add(new_user)
                db.db_session.commit()
            email_cred_to_upd = db.db_session.query(EmailCredential).filter_by(user_id=user_id).first()
            if email_cred_to_upd:
                email_cred_to_upd.email_login = email_login
                email_cred_to_upd.email_passwd = email_passwd
                email_cred_to_upd.pop_server = pop_server
                email_cred_to_upd.smtp_server = smtp_server
                email_cred_to_upd.user_id = user_id
            else:
                new_email_cred = EmailCredential(email_login=email_login,
                                                 email_passwd=email_passwd,
                                                 pop_server=pop_server,
                                                 smtp_server=smtp_server,
                                                 user_id=user_id)
                db.db_session.add(new_email_cred)
                db.db_session.commit()
            return redirect(url_for('user_menu'))
        except Exception as err:
            print(err)

    user_data = db.db_session.query(User).filter_by(id=user_id).first()
    email_cred = db.db_session.query(EmailCredential).filter_by(user_id=user_id).first()
    documents = db.db_session.query(Document).all()
    templates = db.db_session.query(Template).filter_by(user_id=user_id).all()
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
    if not session.get('user_id'):
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    return 'User templates'


if __name__ == '__main__':
    app.secret_key = '!@JkikSPdkp9871jiod89^%&*&Ghuhgu'
    app.run(debug=True, use_reloader=True, host="0.0.0.0", port=5050)
