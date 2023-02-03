from flask import Flask
from flask import render_template

import data
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
    Show all vacancies
    Returns:
        list - list of dictionaries of vacancies
    """
    return render_template('vacancies.html', vacancies=data.vacancies, title='All vacancies')


@app.route('/vacancy/<int:vacancy_id>', methods=['GET', 'PUT'])
def vacancy(vacancy_id):
    """
    Show specific vacancy by ID
    Args:
        vacancy_id: int - id of specific vacancy
    Returns:
        dict - data of specific vacancy
    """
    contact = Contact(vacancy_id)
    for specific_vacancy in data.vacancies:
        if specific_vacancy.get('id', None) == vacancy_id:
            return render_template('vacancy.html',
                                   title=specific_vacancy['position_name'],
                                   data=specific_vacancy,
                                   contacts=contact.get_contacts)


@app.route('/vacancy/<int:vacancy_id>/events', methods=['GET', 'POST'])
def vacancy_events(vacancy_id):
    """
    Show all vacancy's events
    Args:
        vacancy_id: int - ID of specific vacancy
    Returns:
        list - list of event dictionaries
    """
    events_list = []
    for event in data.events:
        if event.get('vacancy_id', None) == vacancy_id:
            events_list.append(event)
    if events_list:
        return events_list


@app.route('/vacancy/<int:vacancy_id>/event/<int:event_id>', methods=['GET', 'PUT'])
def vacancy_event(vacancy_id, event_id):
    """
    Get specific event of specific vacancy
    Args:
        vacancy_id: int
        event_id: int
    Returns:
        dict - dictionary of event's data
    """
    for event in data.events:
        if event['vacancy_id'] == vacancy_id:
            if event.get('id', None) == event_id:
                return event
    return 'No event found'


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
    if data.user:
        return render_template('user.html', title='User menu', menu=data.user)
    return 'No user data'


@app.route('/user/calendar', methods=['GET'])
def user_calendar():
    return 'User calendar'


@app.route('/user/mail', methods=['GET'])
def user_mail():
    return 'User mail'


@app.route('/user/settings', methods=['GET', 'PUT'])
def user_settings():
    return 'User settings'


@app.route('/user/documents', methods=['GET', 'POST', 'PUT'])
def user_documents():
    return data.documents


@app.route('/user/templates', methods=['GET', 'POST', 'PUT'])
def user_templates():
    return 'User templates'


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
