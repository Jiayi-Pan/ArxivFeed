# Arxiv Feed

![Demo](https://i.imgur.com/LDcIGSf.png)

## Overview
Arxiv Feed is a straightforward tool to keep you updated with the latest research papers from Arxiv.org. By selecting your areas of interest, it compiles a digest and delivers it straight to your inbox. 

This service is free and runs on GitHub Actions once a day.


## Setup

1. Fork this repository

2. Update the `config.py` file with your preferences:
    - `subscribers`: Add the emails where you want the digest to be sent.
    - `domains`: Specify your preferred research domains. Check domain codes [here](https://arxiv.org/category_taxonomy).
    - `resend_key`: Add your [Resend email API key.
    ](https://resend.com/). You can also set it up in GitHub Secrets.
    - `num_emails`: Set the number of emails you wish to receive. Each email will contain 1/num_emails of the papers.
    - Example:
        ```python
        subscribers = ["your-email1@example.com", "your-email2@example.com"]
        domains = ["cs.AI", "cs.CV"]
        resend_key = "your-resend-email-API-key"
        num_emails = 3
        ```
3. Enable GitHub Actions for your forked repository by going to the `Actions` tab and clicking on the `I understand my workflows, go ahead and enable them` button.
4. Lastly, to verify that everything is working, click on the `Run workflow` button for the "Daily Job" action under Github Actions tab. You should receive an email with the latest papers from your selected domains.