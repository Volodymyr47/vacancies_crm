vacancies = [
    {
        "id": 1,
        "creation_date": "20.01.2023",
        "user_id": 1,
        "status": 1,
        "company": "SoftServe",
        "contacts_ids": [1, 2],
        "description": "My vacancy description",
        "position_name": "Trainee Python developer",
        "comment": "No response"
    },
    {
        "id": 2,
        "creation_date": "25.01.2023",
        "user_id": 1,
        "status": 1,
        "company": "EPAM",
        "contacts_ids": [3, 4],
        "description": "My vacancy description",
        "position_name": "Junior Python developer",
        "comment": "I have received response"
    },
    {
        "id": 3,
        "creation_date": "01.02.2023",
        "user_id": 1,
        "status": 1,
        "company": "GlobalLogic",
        "contacts_ids": [5, 6],
        "description": "My vacancy description",
        "position_name": "Trainee Python developer",
        "comment": "I have received response"
    }
]

events = [
    {
        "id": 1,
        "vacancy_id": 2,
        "description": "Event description",
        "event_date": "25.01.2023",
        "title": "Event title",
        "due_to_date": "05.02.2023",
        "status": 1
    },
{
        "id": 2,
        "vacancy_id": 1,
        "description": "Event description",
        "event_date": "26.01.2023",
        "title": "Event title",
        "due_to_date": "27.01.2023",
        "status": 1
    },
{
        "id": 3,
        "vacancy_id": 2,
        "description": "Event 3 Test task",
        "event_date": "31.01.2023",
        "title": "New test task",
        "due_to_date": "05.02.2023",
        "status": 1
    }
]

documents = [
    {
        "id": 1,
        "name": "Photo",
        "description": "",
        "content": "Path to UserPhoto",
        "user_id": 1
    },
    {
        "id": 2,
        "name": "CV",
        "description": "My actuality CV",
        "content": "Path to CV",
        "user_id": 1
    }
]

contacts = [
    {
        "id": 1,
        "name": "SoftServe HR",
        "phone": "0961234578",
        "mail": "hr@softserveinc.com"
    },
    {
        "id": 2,
        "name": "SoftServe Senior spec",
        "phone": "0961472558",
        "mail": "spec@softserveinc.com"
    },
{
        "id": 3,
        "name": "EPAM HR",
        "phone": "0970123456",
        "mail": "hr@epam.com"
    },
    {
        "id": 4,
        "name": "EPAM Senior spec",
        "phone": "0931231221",
        "mail": "spec@epam.com",
        "telegram": "@spec_epam"
    }
]

user = [
    {
        "id": 1,
        "name": "Volodymyr Dziadyk",
        "mail": "my_mail@gmail.com",
        "login": "vd_login",
        "passwd": "123456"
    }
]
