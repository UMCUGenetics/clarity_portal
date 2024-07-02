"""Clarity Portal utility functions."""
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from smtplib import SMTP
from mimetypes import guess_type

from tenacity import retry, stop_after_attempt, wait_fixed


class WSGIMiddleware(object):
    """WSGI Middleware."""

    def __init__(self, app, prefix):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        environ['SCRIPT_NAME'] = self.prefix
        return self.app(environ, start_response)


def send_email(sender, receivers, subject, text, attachment=None):
    """Send emails."""
    mail = MIMEMultipart()
    mail['Subject'] = subject
    mail['From'] = sender
    mail['To'] = ';'.join(receivers)

    if attachment:
        filename = attachment.split('/')[-1]
        fp = open(attachment, 'rb')
        ctype, encoding = guess_type(attachment)
        if ctype is None or encoding is not None:
            # No guess could be made, or the file is encoded (compressed), so
            # use a generic bag-of-bits type.
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        msg = MIMEBase(maintype, subtype)
        msg.set_payload(fp.read())
        fp.close()
        # Encode the payload using Base64
        encoders.encode_base64(msg)
        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        mail.attach(msg)

    msg = MIMEText(text)
    mail.attach(msg)

    s = SMTP('smtp-open.umcutrecht.nl')
    s.sendmail(sender, receivers, mail.as_string())
    s.quit()


def char_to_bool(letter):
    """Transform character (J/N) to Bool."""
    if letter.upper() == 'J':
        return True
    elif letter.upper() == 'N':
        return False
    else:
        raise ValueError('Ongeldige letter, alleen J of N toegestaan.')


def transform_sex(value):
    """Transform helix sex/geslacht value to lims sex/geslacht value."""
    if value.strip():
        if value.upper() == 'M':
            return 'Man'
        elif value.upper() == 'V':
            return 'Vrouw'
        elif value.upper() == 'O':
            return 'Onbekend'
        else:
            raise ValueError('Ongeldige letter, alleen M, V of O toegestaan.')
    else:
        return value


def substrings_in_list(substrings, string):
    """Check if substrings are in string."""
    return any(substring in string for substring in substrings)


@retry(stop=stop_after_attempt(2), wait=wait_fixed(1))
def check_lims_connection(lims):
    lims.check_version()
