# Health Check Script for BTCPay Server

This script performs health checks on BTCPay server instances and sends email notifications if an instance is not synchronized or if a server is down.

## Prerequisites

- Python 3.x
- pip (Python package manager)

## Installation

1. **Clone the repository**:

   ```bash
   $ git clone https://github.com/ealvar13/health-check-btcpay.git
   $ cd health-check-btcpay
    ```
2. **Set up a Virtual Environment (Optional but Recommended)**

    ```bash
    $ python -m venv venv
    $ source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```
3. **Install dependencies**

    ```bash
    (venv) $ pip install -r requirements.txt
    ```
## Configuration

1. Create a .env file by copying the .env.example file and adjusting the values to match your environment:

    ```bash
    (venv) $ cp .env.example .env
    ```
    Then, edit .env with your SMTP server settings, BTCPay server URLs, and other configurations as needed.  
    
    Note our example is setup for Gmail and, if you have 2FA enabled, will require an app password.

2. Adjust the logging configuration if necessary. By default, logs are written to btcpay_health_checks.log with a maximum file size of 5MB and up to 2 backup files.

## Running the script
To run the script, ensure you're in the project directory and your virtual environment is activated (if using one). Then execute:

```bash
(venv) $ python health-check-btcpay.py
```

## Scheduling with cron
To run this script at regular intervals, you can set up a cron job. For example, to run the script every day, edit your crontab with crontab -e.

Note this example assumes you are using a Linux server to schedule this task.

First, you need to find the path to your virtual environment to ensure the commands run correctly.

```bash
$ source venv/bin/activate
(venv) $ which python
```

Mark down the location of the virtual environment.

```bash
$ crontab -e
```

Now add a line similar to this to the file:

```bash
30 11 * * * cd /absolute/path/to/your/script/directory && ./path/to/your/venv/bin/python health-check-btcpay.py
```

Save your new crontab and you should be good to go.  You can check if the job was scheduled successfully with:

```bash
$ crontab -l
```

This runs daily at 11:30am in the server local time.  Adjust time and schedule as wanted.   