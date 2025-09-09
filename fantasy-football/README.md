# Fantasy Football Lineup Analyzer

This script fetches your fantasy football lineup data from ESPN, uses the OpenAI API to generate an analysis with lineup recommendations, and sends a report to a specified Slack channel.

## Setup

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Set Environment Variables:**
    You need to set the following environment variables to authenticate with the required services:
    - `ESPN_S2`: Your ESPN authentication cookie.
    - `ESPN_SWID`: Your ESPN software identification cookie.
    - `OPENAI_API_KEY`: Your API key for OpenAI.
    - `SLACK_HOOK`: The webhook URL for the Slack channel where you want to receive reports.

3.  **Configure the Script:**
    Open `main.py` and update the following variables in the configuration section:
    - `league_ids`: A list of your ESPN fantasy football league IDs.
    - `season_year`: The current fantasy football season year.
    - `last_name`: The last name of the team owner to identify your teams.

## Usage

Once the setup is complete, you can run the script with the following command:

```bash
python fantasy-football/main.py
```

The script will then:
1.  Fetch data for the specified leagues.
2.  Identify your teams based on the owner's last name.
3.  Generate an analysis for each team's lineup using OpenAI.
4.  Send a formatted report to your configured Slack channel.
