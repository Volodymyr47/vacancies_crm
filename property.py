import data


class Contact:
    def __init__(self, vacancy_id):
        self.vacancy_id = vacancy_id

    @property
    def get_contacts(self):
        contacts_list = []
        for vacancy in data.vacancies:
            if vacancy['id'] == self.vacancy_id:
                if vacancy.get('contacts_ids', None):
                    vacancy_contact = vacancy.get('contacts_ids')
                    for contact in data.contacts:
                        contacts_list.append(contact) if contact['id'] in vacancy_contact else None
        if not contacts_list:
            contacts_list.append('No contacts found')
        return contacts_list
