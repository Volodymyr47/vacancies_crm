import data


class Contact:
    def __init__(self, vacancy_id):
        self.vacancy_id = vacancy_id

    @property
    def get_contacts(self):
        """
        Get vacancy's contacts.
        Returns:
            list - list of contact's dictionaries
        """
        contacts_list = []
        vacancy_contact = []
        for vacancy in data.vacancies:
            if vacancy.get('id', None) == self.vacancy_id:
                if vacancy.get('contacts_ids', None):
                    vacancy_contact = vacancy.get('contacts_ids')

        for contact in data.contacts:
            contacts_list.append(contact) if contact['id'] in vacancy_contact else None

        if not contacts_list:
            contacts_list.append('No contacts found')
        return contacts_list


class History:
    def __init__(self, vacancy_id):
        self.vacancy_id = vacancy_id
    @property
    def get_history(self):
        events = []
        conversation = ['Test conversation']
        for event in data.events:
            if event.get('vacancy_id', None) == self.vacancy_id:
                events.append(event)
        history_list = {
            "events": events,
            "conversation": conversation
        }
        if not (events and conversation):
            history_list = []
        return history_list
