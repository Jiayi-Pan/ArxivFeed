subscribers = ["jiayidotpan@gmail.com"] # list of subscribers to send emails to
domains = ["cs.AI"] # list of research domains to watch, check https://arxiv.org/category_taxonomy for more info
resend_key = None # You can either set the resend email API key in the environment variable or right here 
num_emails = 3 # number of emails to send, each email contains 1/num_emails of the papers

# do not change the following code
import os
if resend_key is None:
    resend_key = os.environ.get("RESEND_KEY")
