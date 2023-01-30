from flask import Flask
# from flask import request, render_template

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return 'Welcome to Vacancies CRM'


@app.route('/vacancies', methods=['GET', 'POST'])
def vacancies():
    return 'All vacancies'


@app.route('/vacancy/<int:vacancy_id>', methods=['GET', 'PUT'])
def vacancy(vacancy_id):
    return f'Specific vacancy with id {vacancy_id}'


@app.route('/vacancy/<int:vacancy_id>/events', methods=['GET', 'POST'])
def vacancy_events(vacancy_id):
    return f'All events for vacancy with id {vacancy_id}'


@app.route('/vacancy/<int:vacancy_id>/event/<int:event_id>', methods=['GET', 'PUT'])
def vacancy_event(vacancy_id, event_id):
    return f'Specific event with id {event_id} for specific vacancy with id {vacancy_id}'


@app.route('/vacancy/<int:vacancy_id>/history', methods=['GET'])
def vacancy_history(vacancy_id):
    return f'History for specific vacancy with id {vacancy_id}'


@app.route('/user', methods=['GET'])
def user_menu():
    return 'User menu'


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
    return 'User documents'


@app.route('/user/templates', methods=['GET', 'POST', 'PUT'])
def user_templates():
    return 'User templates'


if __name__ == '__main__':
    app.run()
