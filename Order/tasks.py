from celery import shared_task
from django.core.mail import EmailMultiAlternatives

@shared_task
def send_mail(subject,text_content,html_content):
        msg = EmailMultiAlternatives(
            subject,
            text_content,
            "vishnudask410@gmail.com",  # From
            ["vishnudaswork86@gmail.com"],  # To
            headers={"List-Unsubscribe": "vishnudaswork86@gmail.com"},
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        print('email send')