from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from datetime import datetime

from postgresdb import Base


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False, unique=True)
    login = Column(String(50), nullable=False, unique=True)
    passwd = Column(String(120), nullable=False)
    email = Column(String(80), nullable=False, unique=True)

    def __init__(self, name, login, password, email):
        self.name = name
        self.login = login
        self.passwd = password
        self.email = email

    def __repr__(self):
        return f'User {self.name}'


class EmailCredential(Base):
    __tablename__ = 'email_creds'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    email_login = Column(String(120), nullable=False)
    email_passwd = Column(String(120), nullable=False)
    pop_server = Column(String(100), nullable=True)
    pop_port = Column(Integer, nullable=True)
    imap_server = Column(String(100), nullable=True)
    imap_port = Column(Integer, nullable=True)
    smtp_server = Column(String(100), nullable=True)
    smtp_port = Column(Integer, nullable=True)

    def __init__(self, user_id, email_login, email_passwd,
                 pop_server, pop_port,
                 imap_server, imap_port,
                 smtp_server, smtp_port):
        self.user_id = user_id
        self.email_login = email_login
        self.email_passwd = email_passwd
        self.pop_server = pop_server
        self.pop_port = pop_port
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

    def get_smtp_mandatory_fields(self):
        return {'login': self.email_login,
                'password': self.email_passwd,
                'smtp_server': self.smtp_server,
                'smtp_port': self.smtp_port
                }

    def get_pop_mandatory_fields(self):
        return {'login': self.email_login,
                'password': self.email_passwd,
                'pop_server': self.pop_server,
                'pop_port': self.pop_port
                }


class Vacancy(Base):
    __tablename__ = 'vacancy'
    id = Column(Integer, primary_key=True, autoincrement=True)
    creation_date = Column(DateTime, default=datetime.utcnow())
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    position_name = Column(String(120), nullable=False)
    company = Column(String(120), nullable=False)
    contacts_ids = Column(String(120), nullable=True)
    description = Column(Text, nullable=False)
    url = Column(String(150), nullable=True)
    comment = Column(Text, nullable=True)
    status = Column(Integer, nullable=False)

    def __init__(self, position_name, company, description, contacts_ids, comment, url, status, user_id):
        self.position_name = position_name
        self.company = company
        self.description = description
        self.contacts_ids = contacts_ids
        self.comment = comment
        self.url = url
        self.status = status
        self.user_id = user_id

    def __repr__(self):
        return self.position_name


class Event(Base):
    __tablename__ = 'event'
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_date = Column(DateTime, default=datetime.utcnow())
    vacancy_id = Column(Integer, ForeignKey('vacancy.id'), nullable=False)
    title = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Integer, nullable=False)
    due_to_date = Column(String(10), nullable=True)

    def __init__(self, vacancy_id, title, description, status, due_to_date):
        self.vacancy_id = vacancy_id
        self.title = title
        self.description = description
        self.due_to_date = due_to_date
        self.status = status

    def __repr__(self):
        return f'Event {self.title}'


class Document(Base):
    __tablename__ = 'document'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(40), nullable=False)
    description = Column(Text, nullable=True)
    content = Column(String(120), nullable=True)

    def __init__(self, name, description, content):
        self.name = name
        self.description = description
        self.content = content

    def __repr__(self):
        return f'Document {self.name}'


class Template(Base):
    __tablename__ = 'templates'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    name = Column(String(120), nullable=False)
    content = Column(String(120), nullable=False)

    def __init__(self, name, content):
        self.name = name
        self.content = content

    def __repr__(self):
        return self.name
