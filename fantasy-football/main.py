import os
from espn_api.football import League
from openai import OpenAI
import requests
import json
from typing import Dict, List, Union

# Configuration
espn_s2 = os.getenv("ESPN_S2")
swid = os.getenv("ESPN_SWID")
league_ids = [1198961, 1542043, 1004103369, 635235368]  # Example IDs
season_year = 2025
last_name = "Diderich"

# Initialize OpenAI client (set your API key as environment variable: OPENAI_API_KEY)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_league_data() -> List[League]:
    """Fetch league data from ESPN API"""
    leagues = []
    for league_id in league_ids:
        try:
            league = League(
                league_id=league_id, year=season_year, espn_s2=espn_s2, swid=swid
            )
            leagues.append(league)
        except Exception as e:
            print(f"Error fetching league {league_id}: {e}")
    return leagues


def get_team_lineup_data(leagues: List[League]) -> List[Dict]:
    """Get current lineup data for all your teams"""
    team_lineups = []

    for i, league in enumerate(leagues):
        teams = league.teams

        # Find your team in this league
        for team in teams:
            for owner in team.owners:
                if last_name == owner["lastName"]:
                    lineup_data = {
                        "league_id": league_ids[i],
                        "team_name": getattr(
                            team, "team_name", getattr(team, "teamName", f"Team {i+1}")
                        ),
                        "roster": [],
                        "bench": [],
                        "matchup_opponent": None,
                    }

                    for player in team.roster:
                        player_info = {
                            "name": player.name,
                            "position": player.position,
                            "team": player.proTeam,
                            "slot_position": player.lineupSlot,
                            "projected_avg_points": player.projected_avg_points,
                            "avg_points": player.avg_points,
                            "total_points": player.total_points,
                            "injured": player.injured,
                            "injury_status": player.injuryStatus,
                            "percent_owned": player.percent_owned,
                            "percent_started": player.percent_started,
                        }

                        if player.lineupSlot == "BE":
                            lineup_data["bench"].append(player_info)
                        else:
                            lineup_data["roster"].append(player_info)

                    try:
                        matchups = league.scoreboard()
                        for matchup in matchups:
                            if team == matchup.home_team:
                                lineup_data["matchup_opponent"] = getattr(
                                    matchup.away_team,
                                    "team_name",
                                    getattr(
                                        matchup.away_team,
                                        "teamName",
                                        "Unknown Opponent",
                                    ),
                                )
                                break
                            elif team == matchup.away_team:
                                lineup_data["matchup_opponent"] = getattr(
                                    matchup.home_team,
                                    "team_name",
                                    getattr(
                                        matchup.home_team,
                                        "teamName",
                                        "Unknown Opponent",
                                    ),
                                )
                                break
                    except Exception as e:
                        print(f"Could not get matchup info: {e}")
                        lineup_data["matchup_opponent"] = "Unknown"

                    team_lineups.append(lineup_data)
                    break

    return team_lineups


def analyze_lineup_with_openai(lineup_data: Dict) -> Dict:
    """Use OpenAI to analyze lineup and suggest optimizations, returning JSON."""
    system_prompt = """You are an expert fantasy football analyst.
        Your response MUST be a JSON object with the following keys. Each key's value should be either a string or a list of strings (for bullet points).

        **CRITICAL RULES:**
        1.  **NEVER** recommend starting a player whose `injury_status` is 'OUT' or 'IR'.
        2.  **ALWAYS** treat a `projected_avg_points` of 0 as a non-starter.
        3.  Heavily weigh the `injury_status` in all recommendations. A player who is 'Questionable' is a significant risk.

        {
        "overall_analysis": "Your overall summary here.",
        "key_recommendations": [
            "Recommendation 1.",
            "Recommendation 2."
        ],
        "start_sit_suggestions": [
            "Start/Sit suggestion 1.",
            "Start/Sit suggestion 2."
        ],
        "injury_concerns": [
            "Injury concern 1.",
            "Injury concern 2."
        ],
        "risk_assessment": [
            "Risk assessment 1.",
            "Risk assessment 2."
        ],
        "expected_point_improvements": [
            "Improvement 1.",
            "Improvement 2."
        ],
        "overall_team_potential": "Summary of team potential here."
        }

        Ensure all values are valid JSON strings or lists of strings. Be concise but thorough.
        """

    user_prompt = f"""
        TEAM: {lineup_data['team_name']} (League ID: {lineup_data['league_id']})
        OPPONENT: {lineup_data['matchup_opponent']}

        CURRENT STARTING LINEUP:
        {json.dumps(lineup_data['roster'], indent=2)}

        BENCH PLAYERS:
        {json.dumps(lineup_data['bench'], indent=2)}

        Focus on:
        1. Should any bench players be started over current starters?
        2. Best/worst matchups this week.
        3. Injury concerns/news updates.
        4. Expected point improvements from recommended changes.
        """

    try:
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_web",
                    "description": "Search the web for latest player news or matchup stats",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"}
                        },
                        "required": ["query"],
                    },
                },
            }
        ]

        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            tools=tools,
            tool_choice="auto",
        )

        analysis_json = json.loads(response.choices[0].message.content.strip())
        return analysis_json

    except Exception as e:
        print(f"OpenAI API error or JSON parsing error: {e}")
        return {"error": f"OpenAI API error or JSON parsing error: {e}"}


def send_to_slack(report_blocks: List[Dict]):
    """Sends the formatted report blocks to a Slack webhook."""
    slack_hook_url = os.environ.get("SLACK_HOOK")
    if not slack_hook_url:
        print("⚠️ SLACK_HOOK environment variable not set. Cannot send to Slack.")
        return

    payload = {"blocks": report_blocks}

    try:
        response = requests.post(
            slack_hook_url,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )
        if response.status_code == 200:
            print("✅ Successfully sent report to Slack!")
        else:
            print(
                f"❌ Failed to send to Slack. Status code: {response.status_code}, Response: {response.text}"
            )
    except requests.exceptions.RequestException as e:
        print(f"❌ An error occurred while sending to Slack: {e}")


def format_analysis_for_slack(team_name: str, analysis_json: Dict) -> List[Dict]:
    """
    Slack formatter:
    - Formats content from the JSON response using appropriate markdown.
    """

    section_config = {
        "overall_analysis": {"emoji": "📋", "title": "Overall Analysis"},
        "key_recommendations": {"emoji": "✅", "title": "Key Recommendations"},
        "start_sit_suggestions": {"emoji": "🔥", "title": "Start/Sit Suggestions"},
        "injury_concerns": {"emoji": "🚑", "title": "Injury Concerns"},
        "risk_assessment": {"emoji": "⚖️", "title": "Risk Assessment"},
        "expected_point_improvements": {
            "emoji": "📈",
            "title": "Expected Point Improvements",
        },
        "overall_team_potential": {"emoji": "🎯", "title": "Overall Team Potential"},
    }

    blocks: List[Dict] = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🏈 Quick Look: {team_name}",
                "emoji": True,
            },
        },
        {"type": "divider"},
    ]

    # Define the order of sections for display
    ordered_keys = [
        "overall_analysis",
        "key_recommendations",
        "start_sit_suggestions",
        "injury_concerns",
        "risk_assessment",
        "expected_point_improvements",
        "overall_team_potential",
    ]

    for key in ordered_keys:
        if key in analysis_json and analysis_json[key]:
            content = analysis_json[key]
            config = section_config.get(
                key, {"emoji": "•", "title": key.replace("_", " ").title()}
            )

            formatted_content = ""
            if isinstance(content, list):
                # Format list items as Slack markdown bullet points
                formatted_content = "\n".join([f"- {item.strip()}" for item in content])
            else:
                # Use as-is for single string content, ensure it's a string
                formatted_content = str(content).strip()

            if formatted_content:  # Only add if there's actual content
                blocks.append(
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"{config['emoji']} *{config['title']}*\n{formatted_content}",
                        },
                    }
                )
                blocks.append({"type": "divider"})

    # Remove the last divider if it exists and there's content before it
    if blocks and len(blocks) > 2 and blocks[-1]["type"] == "divider":
        blocks.pop()

    blocks.append({"type": "divider"})
    for _ in range(5):
        blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": " " 
        }
    })

    return blocks


def main():
    """Main execution with OpenAI lineup optimization and Slack reporting"""
    try:
        print("Fetching league data...")
        leagues = get_league_data()
        if not leagues:
            print("No leagues found. Check your credentials.")
            return

        print("Getting team lineups...")
        team_lineups = get_team_lineup_data(leagues)

        for i, lineup in enumerate(team_lineups):
            team_name = lineup["team_name"]
            print(f"\n--- Analyzing Team {i+1}: {team_name} ---")

            analysis_json = analyze_lineup_with_openai(lineup)

            # Print the raw JSON response for debugging
            print(
                "\nRaw OpenAI Analysis (JSON):\n", json.dumps(analysis_json, indent=2)
            )

            if "error" in analysis_json:
                print(
                    f"Skipping Slack report due to OpenAI error: {analysis_json['error']}"
                )
                continue

            report_blocks = format_analysis_for_slack(team_name, analysis_json)
            send_to_slack(report_blocks)

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set your OPENAI_API_KEY environment variable")
        exit(1)
    # SLACK_HOOK can be optional for local testing if you don't want to send to Slack
    # if not os.getenv("SLACK_HOOK"):
    #     print("Please set your SLACK_HOOK environment variable")
    #     exit(1)

    main()
