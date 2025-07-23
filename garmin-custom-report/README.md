# Automated Garmin Health Reporter

This project contains a Python script that connects to the Garmin Connect API, fetches your historical health data, performs a comparative analysis, and sends a beautifully formatted weekly report to a Slack channel. The entire process is automated using GitHub Actions.

---

## Features

- **Automated Weekly Reports:** Runs on a schedule every Monday morning.  
- **Comparative Analysis:** Compares your last 30 days of health data against your all‑time average to highlight recent trends.  
- **Comprehensive Metrics:** Tracks key health indicators including Sleep Score, Steps, Resting Heart Rate, Stress, Body Battery, and more.  
- **Secure:** Uses GitHub Repository Secrets to keep your Garmin and Slack credentials safe.  
- **Rich Slack Notifications:** Delivers reports in a clean, easy‑to‑read format using Slack’s Block Kit.  

---

## Project Structure

```

.
├── .github/
│   └── workflows/
│       └── weekly-health-report.yml    ← The GitHub Action workflow
├── garmin-custom-report/
│   ├── main.py                         ← The main Python script
│   └── requirements.txt                ← Python dependencies
└── README.md                           ← This file

````

---

## Setup and Configuration

### 1. Prerequisites

- A GitHub account  
- A Garmin Connect account  
- Python 3.8 or newer installed on your local machine (for testing)  
- A Slack workspace where you can create an incoming webhook  

### 2. Local Setup (for testing)

1. **Clone the repository:**
   ```bash
   git clone <your-repository-url>
   cd <your-repository-name>
````

2. **Create and activate a virtual environment:**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Create a `.env` file** in the root of the project and add your credentials:

   ```dotenv
   # .env
   GARMIN_EMAIL="your-email@example.com"
   GARMIN_PASSWORD="your_garmin_password"
   SLACK_HOOK="https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
   ```

### 3. Slack Webhook Setup

1. Go to the **Slack App Directory** and search for **Incoming WebHooks**.
2. Click **Add to Slack** and choose the channel where you want the report to be posted.
3. Copy the provided **Webhook URL** and use it as the value for `SLACK_HOOK`.

### 4. GitHub Action Automation Setup

#### Configure Repository Secrets

To allow the GitHub Action to run securely without exposing your credentials:

1. In your GitHub repository, go to **Settings > Secrets and variables > Actions**.
2. Click **New repository secret** for each of the following:

   * `GARMIN_EMAIL`: Your Garmin Connect email address
   * `GARMIN_PASSWORD`: Your Garmin Connect password
   * `SLACK_HOOK`: Your Slack incoming webhook URL

---

## Usage

### Running Locally

After setting up your `.env` file, run the script manually to test it:

```bash
python garmin-custom-report/main.py
```

### Automated Reports

* **Scheduled Run:** The action is configured to run every Monday at 8:00 AM Central Time. You can change this schedule by editing the `cron` value in `.github/workflows/weekly-health-report.yml`.
* **Manual Run:** Trigger the report manually by going to the **Actions** tab in your GitHub repository, selecting **Weekly Health Report**, and clicking **Run workflow**.