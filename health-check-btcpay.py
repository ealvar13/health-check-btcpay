#!/usr/bin/env python3

import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import requests
from requests.exceptions import RequestException
import logging
from logging.handlers import RotatingFileHandler

# Create a custom formatter
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Create a RotatingFileHandler
logHandler = RotatingFileHandler('btcpay_health_checks.log', mode='a', maxBytes=5*1024*1024, 
                                 backupCount=2, encoding=None, delay=0)
logHandler.setFormatter(log_formatter)
logHandler.setLevel(logging.INFO)

# Get the root logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
# Add the handler to the logger
logger.addHandler(logHandler)

# Load environment variables from .env file
load_dotenv()

# Email settings from environment variables
smtp_server = os.getenv('SMTP_SERVER')
smtp_port = os.getenv('SMTP_PORT')  # Keep as string for now to check if it's provided
email_username = os.getenv('EMAIL_USERNAME')
email_password = os.getenv('EMAIL_PASSWORD')
from_addr = os.getenv('FROM_ADDR')
to_addr = os.getenv('TO_ADDR')
subject = os.getenv('SUBJECT')
body = os.getenv('BODY')

def send_email(smtp_server, smtp_port, email_username, email_password, from_addr, to_addr, subject, body):
    # Validate configuration
    if not all([smtp_server, smtp_port, email_username, email_password, from_addr, to_addr]):
        print("Error: Email configuration is incomplete.")
        return False

    try:
        smtp_port = int(smtp_port)  # Convert port to integer here
    except ValueError:
        print("Error: SMTP_PORT must be a number.")
        return False

    try:
        # Create MIMEText object
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = from_addr
        msg['To'] = to_addr

        # Send the email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Upgrade the connection to secure
        server.login(email_username, email_password)
        server.sendmail(from_addr, to_addr, msg.as_string())
        return True
    except smtplib.SMTPAuthenticationError:
        print("Error: The server didn't accept the username/password combination.")
    except smtplib.SMTPServerDisconnected:
        print("Error: The server unexpectedly disconnected.")
    except smtplib.SMTPException as e:
        print(f"SMTP error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Always try to close the server connection gracefully
        try:
            server.quit()
        except UnboundLocalError:
            # server might not be defined if the exception occurs before its creation
            pass
        except Exception as e:
            print(f"Failed to close the server connection: {e}")
    return False

def health_checks():
    btcpay_urls = os.getenv("BTCPAY_URLS")
    if not btcpay_urls:
        print("No BTCPay URLs configured.")
        return

    urls_list = btcpay_urls.split(',')

    all_synchronized = True  # Initialize the flag as True

    for url in urls_list:
        logger.info(f"Checking health for: {url}")
        headers = {"accept": "application/json"}
        
        try:
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                logger.info("Request successful.")
                response_data = response.json()
                logger.info(response_data)

                if not response_data.get('synchronized', False):
                    logger.error("Instance not synchronized, sending email...")
                    all_synchronized = False
                    email_sent = send_email(smtp_server, str(smtp_port), email_username, email_password, from_addr, to_addr, "Problem Detected with BTCPay", f"BTCPay server instance at URL {url} is not synchronized.")
                    if email_sent:
                        logger.info("Notification email sent successfully.")
                    else:
                        logger.error("Failed to send notification email.")
            else:
                logger.error(f"Request failed with status code: {response.status_code}")
                all_synchronized = False
                # Send an email indicating the server might be down due to bad response
                logger.error(f"Server might be down, sending email about status code {response.status_code}...")
                email_sent = send_email(smtp_server, str(smtp_port), email_username, email_password, from_addr, to_addr, "BTCPay Server Might Be Down Detected", f"Received a {response.status_code} response from BTCPay server instance at URL {url}. The server might be down.")
                if email_sent:
                    logger.info("Server down notification email sent successfully.")
                else:
                    logger.error("Failed to send server down notification email.")

        except RequestException as e:
            logger.error(f"Failed to connect to {url}. Error: {e}")
            all_synchronized = False
            logger.error("Server is down, sending email...")
            email_sent = send_email(smtp_server, str(smtp_port), email_username, email_password, from_addr, to_addr, "Server Down Detected", f"Failed to connect to BTCPay server instance at URL {url}. It may be down.")
            if email_sent:
                logger.info("Server down notification email sent successfully.")
            else:
                logger.error("Failed to send server down notification email.")

    if all_synchronized:
        logger.info("All instances are synchronized, sending confirmation email...")
        confirmation_sent = send_email(smtp_server, str(smtp_port), email_username, email_password, from_addr, to_addr, "All BTCPay Servers Synchronized", "All BTCPay server instances are synchronized.")
        if confirmation_sent:
            logger.info("Confirmation email sent successfully.")
        else:
            logger.error("Failed to send confirmation email.")

def main():
    health_checks()

if __name__ == "__main__":
    main()
