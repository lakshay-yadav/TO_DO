import threading
from django.core.mail import send_mail
from decouple import config


class EmailThread(threading.Thread):
    def __init__(self, subject, message, from_email, recipient_list):
        self.subject = subject
        self.message = message
        self.from_email = config("MY_EMAIL")
        self.recipient_list = recipient_list
        threading.Thread.__init__(self)

    def run(self):
        send_mail(self.subject, self.message, self.from_email, self.recipient_list)

def send_email_async(subject, message, from_email, recipient_list):
    EmailThread(subject, message, from_email, recipient_list).start()
