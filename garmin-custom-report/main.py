import os
import getpass
import json
import requests
from datetime import date, datetime, timedelta
from pathlib import Path
from garmy import AuthClient, APIClient
from dotenv import load_dotenv


def _calculate_averages(summaries):
    """Helper function to calculate averages for a list of summaries."""
    if not summaries:
        return None

    metrics = {
        "total_steps": 0,
        "total_calories": 0,
        "total_active_calories": 0,
        "total_distance_km": 0,
        "total_resting_hr": 0,
        "total_min_hr": 0,
        "total_max_hr": 0,
        "total_avg_stress": 0,
        "total_max_stress": 0,
        "total_bb_charged": 0,
        "total_bb_drained": 0,
        "total_avg_spo2": 0,
        "total_lowest_spo2": 0,
        "total_avg_resp": 0,
        "total_sleep_score": 0,
    }
    days_with_data = {key: 0 for key in metrics}

    for data in summaries:
        summary = data.get("summary")
        sleep_info = data.get("sleep")

        if not summary:
            continue

        # Check if the underlying attribute is not None before using it
        if summary.total_steps is not None:
            metrics["total_steps"] += summary.total_steps
            days_with_data["total_steps"] += 1
        if summary.total_kilocalories is not None:
            metrics["total_calories"] += summary.total_kilocalories
            days_with_data["total_calories"] += 1
        if summary.active_kilocalories is not None:
            metrics["total_active_calories"] += summary.active_kilocalories
            days_with_data["total_active_calories"] += 1
        if summary.total_distance_meters is not None:
            metrics["total_distance_km"] += summary.distance_km
            days_with_data["total_distance_km"] += 1
        if summary.resting_heart_rate is not None:
            metrics["total_resting_hr"] += summary.resting_heart_rate
            days_with_data["total_resting_hr"] += 1
        if summary.min_heart_rate is not None:
            metrics["total_min_hr"] += summary.min_heart_rate
            days_with_data["total_min_hr"] += 1
        if summary.max_heart_rate is not None:
            metrics["total_max_hr"] += summary.max_heart_rate
            days_with_data["total_max_hr"] += 1
        if (
            summary.average_stress_level is not None
            and summary.average_stress_level > 0
        ):
            metrics["total_avg_stress"] += summary.average_stress_level
            days_with_data["total_avg_stress"] += 1
        if summary.max_stress_level is not None:
            metrics["total_max_stress"] += summary.max_stress_level
            days_with_data["total_max_stress"] += 1
        if summary.body_battery_charged_value is not None:
            metrics["total_bb_charged"] += summary.body_battery_charged_value
            days_with_data["total_bb_charged"] += 1
        if summary.body_battery_drained_value is not None:
            metrics["total_bb_drained"] += summary.body_battery_drained_value
            days_with_data["total_bb_drained"] += 1
        if summary.average_spo2 is not None and summary.average_spo2 > 0:
            metrics["total_avg_spo2"] += summary.average_spo2
            days_with_data["total_avg_spo2"] += 1
        if summary.lowest_spo2 is not None and summary.lowest_spo2 > 0:
            metrics["total_lowest_spo2"] += summary.lowest_spo2
            days_with_data["total_lowest_spo2"] += 1
        if summary.avg_waking_respiration_value is not None:
            metrics["total_avg_resp"] += summary.avg_waking_respiration_value
            days_with_data["total_avg_resp"] += 1

        # Access the nested sleep score from the debug info
        if (
            sleep_info
            and hasattr(sleep_info, "sleep_summary")
            and sleep_info.sleep_summary
            and hasattr(sleep_info.sleep_summary, "sleep_scores")
        ):

            sleep_scores = sleep_info.sleep_summary.sleep_scores
            if (
                sleep_scores
                and "overall" in sleep_scores
                and "value" in sleep_scores["overall"]
            ):
                score = sleep_scores["overall"]["value"]
                if score is not None:
                    metrics["total_sleep_score"] += score
                    days_with_data["total_sleep_score"] += 1

    avg_metrics = {}
    for key, total in metrics.items():
        days = days_with_data[key]
        avg_metrics[key] = total / days if days > 0 else 0

    return avg_metrics


def format_comparative_analysis_for_slack(last_30_days_summaries, all_time_summaries):
    """
    Formats a comparative analysis into a list of Slack blocks with a single-column layout.
    """
    last_30_avg = _calculate_averages(last_30_days_summaries)
    all_time_avg = _calculate_averages(all_time_summaries)

    if not last_30_avg or not all_time_avg:
        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "❌ Not enough data for a comparative analysis.",
                },
            }
        ]

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📈 Daily Health Trends",
                "emoji": True,
            },
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Comparing the *Last 30 Days* vs. your *All-Time* average. Report generated on {date.today().strftime('%B %d, %Y')}.",
                }
            ],
        },
        {"type": "divider"},
    ]

    metrics_to_compare = [
        ("Steps", "total_steps", ",.0f", "👟"),
        ("Distance (km)", "total_distance_km", ".2f", "📏"),
        ("Sleep Score", "total_sleep_score", ".1f", "😴"),
        ("Total Calories (kcal)", "total_calories", ",.0f", "🔥"),
        ("Active Calories (kcal)", "total_active_calories", ",.0f", "💪"),
        ("Resting HR (bpm)", "total_resting_hr", ".1f", "❤️"),
        ("Avg Stress", "total_avg_stress", ".1f", "😌"),
        ("Avg Max Stress", "total_max_stress", ".1f", "😟"),
        ("Body Battery Charged", "total_bb_charged", ".1f", "🔋+"),
        ("Body Battery Drained", "total_bb_drained", ".1f", "🔋-"),
        ("Avg SpO2 (%)", "total_avg_spo2", ".1f", "🫁"),
        ("Avg Respiration (brpm)", "total_avg_resp", ".1f", "🌬️"),
    ]

    for name, key, fmt, icon in metrics_to_compare:
        val_30 = last_30_avg.get(key, 0)
        val_all = all_time_avg.get(key, 0)

        # Format the numbers first
        val_30_formatted = f"{val_30:{fmt}}"
        val_all_formatted = f"{val_all:{fmt}}"

        # Determine which value is larger and make it bold
        if val_30 > val_all:
            val_30_str = f"*{val_30_formatted}*"
            val_all_str = val_all_formatted
        elif val_all > val_30:
            val_30_str = val_30_formatted
            val_all_str = f"*{val_all_formatted}*"
        else:  # They are equal
            val_30_str = val_30_formatted
            val_all_str = val_all_formatted

        # Determine the percentage change
        change_str = " "  # Default space
        if val_all > 0 and val_30 > 0:
            percent_change = ((val_30 - val_all) / val_all) * 100
            if abs(percent_change) > 2:
                arrow = "🔼" if percent_change > 0 else "🔽"
                change_str = f"_{arrow} {percent_change:+.1f}%_"

        field_text = (
            f"*{icon} {name}*\n"
            f"{val_30_str} (30d) vs {val_all_str} (All Time) {change_str}"
        )

        # Create a new section block for each metric
        metric_block = {
            "type": "section",
            "text": {"type": "mrkdwn", "text": field_text},
        }
        blocks.append(metric_block)

    return blocks


def send_to_slack(report_blocks):
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


def main():
    """
    Main function to fetch Garmin data, format it, and send it to Slack.
    """
    load_dotenv()

    try:
        email = os.environ.get("GARMIN_EMAIL")
        password = os.environ.get("GARMIN_PASSWORD")

        if not email or not password:
            print("\nCould not find credentials in environment variables.")
            email = input("Enter your Garmin Connect email: ")
            password = getpass.getpass("Enter your Garmin Connect password: ")

        print("\nConnecting to Garmin Connect...")
        auth_client = AuthClient()
        api_client = APIClient(auth_client=auth_client)

        auth_client.login(email, password)
        print("Successfully connected!")

        days_to_fetch = 365
        print(f"\nFetching data for the last {days_to_fetch} days...")

        summary_accessor = api_client.metrics.get("daily_summary")
        sleep_accessor = api_client.metrics.get("sleep")

        if not summary_accessor or not sleep_accessor:
            print("❌ Daily summary or sleep metric not available in the library.")
            return

        all_summaries = summary_accessor.list(days=days_to_fetch)
        all_sleep_data = sleep_accessor.list(days=days_to_fetch)

        if not all_summaries:
            print("❌ No historical summary data found.")
            return

        # Merge summary and sleep data
        merged_data = {}
        for summary in all_summaries:
            merged_data[summary.calendar_date] = {"summary": summary, "sleep": None}

        for sleep_info in all_sleep_data:
            # Using the correct path found from the debug info
            if hasattr(sleep_info, "sleep_summary") and sleep_info.sleep_summary:
                date_key = sleep_info.sleep_summary.calendar_date
                if date_key in merged_data:
                    merged_data[date_key]["sleep"] = sleep_info

        # Convert merged data back to a list, sorted by date
        combined_list = list(merged_data.values())
        combined_list.sort(key=lambda x: x["summary"].calendar_date, reverse=True)

        last_30_days_data = combined_list[:30]
        all_time_baseline_data = combined_list[30:]

        # Format the report into Slack blocks
        report_blocks = format_comparative_analysis_for_slack(
            last_30_days_data, all_time_baseline_data
        )

        # Send the report to Slack
        send_to_slack(report_blocks)

    except Exception as e:
        print(f"\nAn error occurred: {e}")
        import traceback

        traceback.print_exc()
        print(
            "\nPlease check your credentials and ensure you have a stable internet connection."
        )
        print(
            "If the error persists, the data structure from the API may have changed."
        )


if __name__ == "__main__":
    main()
