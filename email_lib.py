from smtplib import SMTP_SSL
from poplib import POP3_SSL
from imaplib import IMAP4_SSL
from email.parser import Parser
from email.header import decode_header
import email


class EmailWrapper:
    def __init__(
                 self, login, password,
                 pop_server=None, pop_port=995,
                 imap_server=None, imap_port=993,
                 smtp_server=None, smtp_port=465
                 ):
        self.login = login,
        self.passwd = password,
        # self.email = email,
        self.pop_server = pop_server,
        self.pop_port = pop_port,
        self.imap_server = imap_server,
        self.imap_port = imap_port,
        self.smtp_server = smtp_server,
        self.smtp_port = smtp_port

    @staticmethod
    def _decode_str(s):
        value, charset = decode_header(s)[0]
        if charset:
            value = value.decode(charset)
        return value

    def get_mail_by_pop(self, msg_type='html'):
        result = {}
        pop_serv = POP3_SSL(self.pop_server[0])
        pop_serv.port = 995
        pop_serv.user(self.login[0])
        pop_serv.pass_(self.passwd[0])

        number_of_msg = len(pop_serv.list()[1])

        for i in range(number_of_msg):
            lines = pop_serv.retr(i+1)[1]
            msg_content = b'\r\n'.join(lines).decode('latin1')
            msg = Parser().parsestr(msg_content)

            try:
                email_subject = msg.get('Subject', 'subject')
                email_subject = self._decode_str(email_subject)

                email_to = msg.get('To')
                if email_to:
                    start_idx_email_to = str(email_to).find('<')
                    latest_idx_email_to = str(email_to).find('>')
                    email_to_str = str(email_to)[start_idx_email_to + 1:latest_idx_email_to]
                    email_to = email_to if len(email_to) < len(email_to_str) else email_to_str
                else:
                    email_to = 'Unknown'

                email_from = msg.get('From')
                if email_from:
                    start_idx_email_from = str(email_from).find('<')
                    latest_idx_email_from = str(email_from).find('>')
                    email_from_str = str(email_from)[start_idx_email_from + 1:latest_idx_email_from]
                    email_from = email_from if len(email_from) > len(email_from_str) else email_from_str
                else:
                    email_from = 'Unknown'

                for line in msg.walk():
                    if line.get_content_type() == f'text/{msg_type}':
                        content = email.message_from_string(line.get_payload(decode=True).decode('utf-8'))
                else:
                    content = email.message_from_string(line.get_payload(decode=True).decode('utf-8'))

                result.update({i: {
                    'email_from': email_from,
                    'email_to': email_to,
                    'email_subject': email_subject,
                    'content': content
                }})
            except UnicodeDecodeError as err:
                print(f'UnicodeDecodeError\n{err}')
            except Exception as exp:
                print(f'Exception\n{exp}')
                continue
        return result

    def get_mail_by_imap(self):
        imap_server = IMAP4_SSL(self.imap_server[0])
        imap_server.login(self.login[0], self.passwd[0])
        imap_server.select('inbox')

        typ, data = imap_server.search(None, 'ALL')
        for num in data[0].split():
            typ, data = imap_server.fetch(num, '(RFC822)')
            print('Message %s\n%s\n' % (num, data[0][1]))
        imap_server.close()
        imap_server.logout()

    def send_mail(self, recipient, subject, message):
        msg = email.message.EmailMessage()
        msg['To'] = recipient
        msg['From'] = self.login
        msg['Subject'] = subject
        msg.set_content(message)
        with SMTP_SSL(self.smtp_server[0], self.smtp_port) as smtp:
            smtp.login(self.login[0], self.passwd[0])
            smtp.send_message(msg)
