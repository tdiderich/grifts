# Garmin Health Report

This script connects to the Garmin Connect API to fetch your historical health data, performs a comparative analysis, and sends a formatted report to a Slack channel.

---

## Features

- **Comparative Analysis:** Compares your last 30 days of health data against your all-time average to highlight recent trends.
- **Comprehensive Metrics:** Tracks key health indicators including Average Stress, HRV, Sleep Score, and Resting Heart Rate.
- **Secure:** Can be configured using environment variables to keep your Garmin and Slack credentials safe.
- **Rich Slack Notifications:** Delivers reports in a clean, easy-to-read format using Slack’s Block Kit.

---

## Project Structure

```
.
├── .github/
│   └── workflows/
│       └── weekly-garmin-report.yaml    ← The GitHub Action workflow
├── garmin-custom-report/
│   └── main.py                         ← The main Python script
├── requirements.txt                    ← Python dependencies
└── README.md                           ← This file
```

---

## Setup and Configuration

### 1. Prerequisites

- A Garmin Connect account.
- Python 3.8 or newer.
- A Slack workspace with an incoming webhook.

### 2. Local Setup

1.  **Clone the repository and navigate to the project root.**

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies from the root of the project:**
    ```bash
    pip install -r requirements.txt
    ```

### 3. Slack Webhook Setup

1.  Go to the **Slack App Directory** and search for **Incoming WebHooks**.
2.  Click **Add to Slack** and choose the channel where you want the report to be posted.
3.  Copy the provided **Webhook URL**.

---

## Usage

This script can be run in two ways:

### Option 1: Using Environment Variables (Recommended)

Create a `.env` file in the root of the project and add your credentials. This is the most secure way to run the script, especially for automated workflows.

```dotenv
# .env
GARMIN_EMAIL="your-email@example.com"
GARMIN_PASSWORD="your_garmin_password"
SLACK_HOOK="https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
```

Then, run the script:

```bash
python garmin-custom-report/main.py
```

### Option 2: Interactive Mode

If you run the script without setting the `GARMIN_EMAIL` and `GARMIN_PASSWORD` environment variables, it will prompt you to enter them in the terminal.

```bash
python garmin-custom-report/main.py
```

### GitHub Actions Automation

The project includes a GitHub Actions workflow (`.github/workflows/weekly-garmin-report.yaml`) that can be configured to run the script on a schedule. To use it, you must configure the following repository secrets in your GitHub repository settings:

- `GARMIN_EMAIL`
- `GARMIN_PASSWORD`
- `SLACK_HOOK`
