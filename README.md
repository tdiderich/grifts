# Grifts - Personal Scripts

This repository contains a collection of personal scripts designed to automate various tasks, from health data analysis to fantasy football lineup recommendations.

## Scripts

### Garmin Custom Report

-   **File:** `garmin-custom-report/main.py`
-   **Description:** This script connects to Garmin Connect, fetches your daily health data (stress, sleep, HRV, resting HR), and calculates a 30-day average versus your all-time average. The comparative analysis is then formatted and sent to a Slack channel.
-   **Automation:** A GitHub Action is configured to run this script weekly. See `.github/workflows/weekly-garmin-report.yaml`.

#### Usage

To run this script, you need to set the following environment variables:

-   `GARMIN_EMAIL`: Your Garmin Connect email address.
-   `GARMIN_PASSWORD`: Your Garmin Connect password.
-   `SLACK_HOOK`: The webhook URL for the Slack channel where you want to post the report.

### Fantasy Football Analysis

-   **File:** `fantasy-football/main.py`
-   **Description:** This script fetches your team's lineup data from ESPN's fantasy football API for all your leagues. It then uses the OpenAI API to analyze your lineup and provide start/sit recommendations and other optimizations. The analysis is then posted to a Slack channel.
-   **Automation:** A GitHub Action is configured to run this script every Tuesday at 12pm CST. See `.github/workflows/weekly-fantasy-football-report.yaml`.

#### Usage

To run this script, you need to set the following environment variables:

-   `ESPN_S2`: Your ESPN `espn_s2` cookie.
-   `ESPN_SWID`: Your ESPN `SWID` cookie.
-   `OPENAI_API_KEY`: Your API key for OpenAI.
-   `SLACK_HOOK`: The webhook URL for the Slack channel.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd grifts
    ```

2.  **Install dependencies:**
    It is recommended to use a virtual environment.
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Set up environment variables:**
    For local development, you can create a `.env` file in the root of the project and add the required variables for the script you want to run.
    ```
    # .env file example
    GARMIN_EMAIL="your-email@example.com"
    GARMIN_PASSWORD="your-password"
    SLACK_HOOK="https://hooks.slack.com/services/..."
    ESPN_S2="your-espn-s2-cookie"
    # ... and so on
    ```
    The scripts use the `python-dotenv` library to load these variables automatically.

## Automation

The scripts are designed to be run automatically using GitHub Actions. The workflow files are located in the `.github/workflows` directory.

For the automation to work, you must configure the following secrets in your GitHub repository's settings (`Settings > Secrets and variables > Actions`):

-   `GARMIN_EMAIL`
-   `GARMIN_PASSWORD`
-   `ESPN_S2`
-   `ESPN_SWID`
-   `OPENAI_API_KEY`
-   `SLACK_HOOK`
