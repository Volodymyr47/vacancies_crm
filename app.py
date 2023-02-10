from flask import Flask, flash
from flask import render_template, request, redirect, url_for

from datetime import datetime

import data
from data import VacancyDataBase
from library import Contact, History


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
def vacancies():
    """
    Get all vacancies and post new vacancy function
    Returns:
        list - list of dictionaries of vacancies
    """
    if request.method == 'POST':
        if request.form.get('position_name', '').strip() == '':
            flash('Field "Position name" must be populated', category='danger')
            return redirect(url_for('vacancies'))
        if request.form.get('company', '').strip() == '':
            flash('Field "Company" must be populated', category='danger')
            return redirect(url_for('vacancies'))
        if request.form.get('description', '').strip() == '':
            flash('Field "Description" must be populated', category='danger')
            return redirect(url_for('vacancies'))

        position_name = request.form.get('position_name')
        company = request.form.get('company')
        description = request.form.get('description')
        contacts = '4, 5, 6'
        comment = request.form.get('comment')
        url = request.form.get('url')
        creation_date = datetime.now().strftime('%Y-%m-%d %H:%m')
        vacancy_data = {
                        'position_name': position_name,
                        'company': company,
                        'description': description,
                        'contacts_ids': contacts,
                        'creation_date': creation_date,
                        'comment': comment,
                        'status': 1,
                        'user_id': 1,
                        'url': url
                        }
        with VacancyDataBase('vacancies.db') as db:
            db.insert('vacancy', vacancy_data)
    with VacancyDataBase('vacancies.db') as db:
        all_vacancies = db.select('vacancy',
                                  order_by='id desc')
    return render_template('vacancies.html',
                           title='All vacancies',
                           vacancies=all_vacancies)


@app.route('/vacancy/<int:vacancy_id>', methods=['GET', 'POST'])
def vacancy(vacancy_id):
    """
    Show/Edit specific vacancy by ID
    Args:
        vacancy_id: int - id of specific vacancy
    Returns:
        dict - data of specific vacancy
    """
    contact = Contact(vacancy_id)

    if request.method == 'POST':
        if request.form.get('position_name', '').strip() == '':
            flash('Field "Position name" must be populated', category='danger')
            return redirect(url_for('vacancies'))
        if request.form.get('company', '').strip() == '':
            flash('Field "Company" must be populated', category='danger')
            return redirect(url_for('vacancies'))
        if request.form.get('description', '').strip() == '':
            flash('Field "Description" must be populated', category='danger')
            return redirect(url_for('vacancies'))

        position_name = request.form.get('position_name')
        company = request.form.get('company')
        description = request.form.get('description')
        contacts = '4, 5, 6'
        comment = request.form.get('comment')
        url = request.form.get('url')
        status = request.form.get('status')
        upd_vacancy_data = {
            'position_name': position_name,
            'company': company,
            'description': description,
            'contacts_ids': contacts,
            'comment': comment,
            'url': url,
            'status': status
        }
        with VacancyDataBase('vacancies.db') as db:
            db.update('vacancy', upd_vacancy_data, condition=f'id = {vacancy_id}')

    with VacancyDataBase('vacancies.db') as db:
        specific_vacancy = db.select('vacancy',
                                     condition=f'id = {vacancy_id}')
    return render_template('vacancy.html',
                           title=specific_vacancy[0]["position_name"],
                           specific_vacancy=specific_vacancy,
                           contacts=contact.get_contacts)


@app.route('/vacancy/<int:vacancy_id>/events', methods=['GET', 'POST'])
def vacancy_events(vacancy_id):
    """
    Show/Edit all vacancy's events
    Args:
        vacancy_id: int - ID of specific vacancy
    Returns:
        list - list of events
    """
    if request.method == 'POST':
        if request.form.get('title', '').strip() == '':
            flash('Field "Title" must be populated', category='danger')
        new_event = {
                    'vacancy_id': vacancy_id,
                    'event_date': datetime.now().strftime('%Y-%m-%d %H:%m'),
                    'title': request.form.get('title'),
                    'description': request.form.get('description'),
                    'due_to_date': request.form.get('due_to_date'),
                    'status': 1
                    }
        with VacancyDataBase('vacancies.db') as db:
            db.insert('event', new_event)
    with VacancyDataBase('vacancies.db') as db:
        events = db.select('event',
                           condition=f'vacancy_id={vacancy_id}',
                           order_by='event_date desc')
        vacancy_name = db.select('vacancy', condition=f'id = {vacancy_id}')[0]['position_name']
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
    if request.method == 'POST':
        if request.form.get('title', '').strip() == '':
            flash('Field "Title" must be populated', category='danger')
        if request.form.get('status', '').strip() == '':
            flash('Field "Status" must be populated', category='danger')

        title = request.form.get('title')
        description = request.form.get('description')
        due_to_date = request.form.get('due_to_date')
        status = request.form.get('status')
        upd_event_data = {
            'title': title,
            'description': description,
            'due_to_date': due_to_date,
            'status': status
        }

        with VacancyDataBase('vacancies.db') as db:
            db.update('event',
                      dataset=upd_event_data,
                      condition=f'id = {event_id} and vacancy_id = {vacancy_id}')

    with VacancyDataBase('vacancies.db') as db:
        specific_event = db.select('event',
                                   condition=f'vacancy_id = {vacancy_id} and id = {event_id}')
    return render_template('event.html',
                           title = specific_event[0]['title'],
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
    history = History(vacancy_id).get_history
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
    with VacancyDataBase('vacancies.db') as db:
        user_data = db.select('user')
        documents = db.select('document')
        templates = db.select('templates')

    return render_template('user.html',
                           title='User menu',
                           user_data=user_data,
                           documents=documents,
                           templates=templates)


@app.route('/user/calendar', methods=['GET'])
def user_calendar():
    return 'User calendar'


@app.route('/user/mail', methods=['GET'])
def user_mail():
    return 'User mail'


@app.route('/user/settings', methods=['GET', 'POST'])
def user_settings():

    if request.method == 'POST':
        if request.form.get('user_name', '').strip() == '':
            flash('Field "Name" must be populated', category='danger')
        if request.form.get('login', '').strip() == '':
            flash('Field "Login" must be populated', category='danger')
        if request.form.get('passwd', '').strip() == '':
            flash('Field "Password" must be populated', category='danger')
        if request.form.get('email', '').strip() == '':
            flash('Field "Email" must be populated', category='danger')

        user_name = request.form.get('user_name')
        login = request.form.get('login')
        passwd = request.form.get('passwd')
        email = request.form.get('email')

        # if request.form.get('photo'):
        #     photo = request.form.get('photo')
        #     photo_name = 'user_photo'
        #     description = 'photo_description'
        # cv = request.form.get('CV')
        # template = request.form.get('template')

        user_data = {
            'name': user_name,
            'login': login,
            'passwd': passwd,
            'email': email
        }
        with VacancyDataBase('vacancies.db') as db:
            db.update('user',
                      dataset=user_data,
                      condition='id = 1')

    with VacancyDataBase('vacancies.db') as db:
        user_data = db.select('user')
        documents = db.select('document')
        templates = db.select('templates')

    return render_template('user-settings.html',
                           title='User menu',
                           user_data=user_data,
                           documents=documents,
                           templates=templates)


@app.route('/user/documents', methods=['GET', 'POST'])
def user_documents():
    return data.documents


@app.route('/user/templates', methods=['GET', 'POST'])
def user_templates():
    return 'User templates'


if __name__ == '__main__':
    app.secret_key = '!@JkikSPdkp9871jiod89^%&*&Ghuhgu'
    app.run(debug=True, use_reloader=True)
