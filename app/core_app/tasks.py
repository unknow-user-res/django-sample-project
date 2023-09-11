from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.core.mail import EmailMultiAlternatives


# send email template test
@shared_task
def send_email_template_test(email):
    from_email = settings.EMAIL_HOST_USER
    to = email
    subject = "Test send email template"
    html_content = render_to_string("email_template.html", {"name": "Nguyen Van A"})
    text_content = strip_tags(html_content)
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    return "Send email template success!"
