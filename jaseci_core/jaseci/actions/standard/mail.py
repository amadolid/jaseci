from jaseci.actions.live_actions import jaseci_action
from jaseci.utils.email_hook import email_hook as eh


@jaseci_action()
def send(sender, recipients, subject, text, html):
    if eh.emailer_running():
        eh.emailer().send_custom_email(sender, recipients, subject, (text, html))
