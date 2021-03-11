from django.apps import apps
EmailConfig = apps.get_model('main', 'EmailConfig')
from django.conf import settings
from django.core.mail import send_mail


def email(username, email):
    if EmailConfig.objects.exists():
        passwd = EmailConfig.objects.all().values_list('default_user_password', flat=True)[0]
    else:
        passwd = settings.DEFAULT_PASSWORD
    subject = 'You account has been created on Bookwallah Dashboard'
    message = '''Below are the credentials for you to connect to login at http://bookwallahdashboard.org
                ''' + '\n\nUsername: ' + username + '\nPassword ' + passwd + '''
                \n\n\nNOTE: Kindly Reset your password after Logging in ASAP.'''

    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)