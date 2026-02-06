import os
import csv
import json
import argparse
import requests
import praw

POSTED_CSV = "shark_tweets.csv"
SUBREDDIT_NAME = "aleximinal"
DORSAL_API_URL = "https://www.dorsalwatch.com/api/public/report/list"
DORSAL_PUBLIC_KEY = "ab61cd9427bea80f22e641c04c312195"
SEARCH_LOCATION = "manly"

# Post Dorsal shark alerts for Manly Beach to Reddit


def get_posted_ids():
    """Read previously posted report IDs from the CSV file."""
    ids = set()
    if os.path.exists(POSTED_CSV):
        with open(POSTED_CSV, "r") as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header
            for row in reader:
                if row:
                    ids.add(row[0])
    return ids


def save_posted_id(report_id):
    """Append a report ID to the CSV file."""
    file_exists = os.path.exists(POSTED_CSV)
    with open(POSTED_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["report_id"])
        writer.writerow([report_id])


def get_reddit_client():
    """Create and return a PRAW Reddit instance."""
    return praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        username=os.getenv("REDDIT_USERNAME"),
        password=os.getenv("REDDIT_PASSWORD"),
        user_agent=os.getenv("REDDIT_USER_AGENT"),
    )


def fetch_shark_reports():
    """Fetch shark reports for Manly Beach from the Dorsal API."""
    payload = {
        "location": SEARCH_LOCATION,
        "timeRange": 0,
        "pageIndex": 0,
        "pageSize": 100,
        "publicKey": DORSAL_PUBLIC_KEY,
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://www.dorsalwatch.com",
        "Referer": "https://www.dorsalwatch.com/report/",
    }

    response = requests.post(DORSAL_API_URL, json=payload, headers=headers)
    response.raise_for_status()

    data = response.json()
    reports = data.get("responseData", [])
    print(f"Fetched {len(reports)} report(s) for '{SEARCH_LOCATION}' from Dorsal")

    for r in reports:
        print(f"  [{r['id']}] {r['formattedReportTime']} - {r['typeOfEncounter']} - {r['comment'][:120]}")

    return reports


def format_report_body(report):
    """Format a Dorsal report into a Reddit post body."""
    parts = []

    if report.get("comment"):
        parts.append(report["comment"])

    details = []
    if report.get("typeOfEncounter"):
        details.append(f"**Type:** {report['typeOfEncounter']}")
    if report.get("typeOfShark"):
        details.append(f"**Shark:** {report['typeOfShark']}")
    if report.get("sharkLength"):
        details.append(f"**Length:** {report['sharkLength']}m")
    if report.get("distanceFromShore") and report["distanceFromShore"] != "N/A":
        details.append(f"**Distance from shore:** {report['distanceFromShore']}m")
    if report.get("formattedReportTime"):
        details.append(f"**Reported:** {report['formattedReportTime']}")

    if details:
        parts.append("\n".join(details))

    dorsal_url = f"https://www.dorsalwatch.com/report/index.html?id={report['id']}"
    parts.append(f"[Source - Dorsal Watch]({dorsal_url})")

    return "\n\n".join(parts)


def post_report_to_reddit(reddit, report):
    """Post a shark report as a self-text post to the subreddit."""
    subreddit = reddit.subreddit(SUBREDDIT_NAME)

    comment = report.get("comment", "")
    shark_type = report.get("typeOfShark", "")
    encounter = report.get("typeOfEncounter", "")
    date = report.get("formattedReportTime", "")

    # Build a descriptive title
    title_parts = [f"Shark Alert - Manly Beach - {date}"]
    if shark_type:
        title_parts.append(f"({shark_type})")
    if encounter:
        title_parts.append(f"- {encounter}")
    title = " ".join(title_parts)
    if len(title) > 300:
        title = title[:297] + "..."

    body = format_report_body(report)

    try:
        subreddit.submit(title, selftext=body)
        print(f"Posted report {report['id']} to r/{SUBREDDIT_NAME}")
        return True
    except Exception as e:
        print(f"Error posting report {report['id']} to r/{SUBREDDIT_NAME}: {e}")
        return False


def main(seed_only=False):
    """
    Main entry point.

    Args:
        seed_only: If True, fetch reports and save IDs without posting to Reddit.
                   Use this to seed the CSV with existing report IDs before going live.
    """
    posted_ids = get_posted_ids()
    print(f"Loaded {len(posted_ids)} previously posted report ID(s)")

    reports = fetch_shark_reports()

    if seed_only:
        new_count = 0
        for report in reports:
            report_id = str(report["id"])
            if report_id in posted_ids:
                print(f"Skipping already saved report {report_id}")
                continue

            save_posted_id(report_id)
            posted_ids.add(report_id)
            new_count += 1
            print(f"Saved report {report_id} (seed mode - not posting to Reddit)")

        print(f"Done. Seeded {new_count} new report ID(s) to {POSTED_CSV}")
        return

    reddit = get_reddit_client()

    new_count = 0
    for report in reports:
        report_id = str(report["id"])
        if report_id in posted_ids:
            print(f"Skipping already posted report {report_id}")
            continue

        if post_report_to_reddit(reddit, report):
            save_posted_id(report_id)
            posted_ids.add(report_id)
            new_count += 1

    print(f"Done. Posted {new_count} new report(s) to r/{SUBREDDIT_NAME}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Post Dorsal shark alerts for Manly Beach to Reddit"
    )
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Seed mode: fetch reports and save IDs without posting to Reddit. "
             "Run this once to capture existing report IDs before going live.",
    )
    args = parser.parse_args()
    main(seed_only=args.seed)
