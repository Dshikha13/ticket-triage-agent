import json
import os
import ssl
import certifi
from dotenv import load_dotenv
from jira import JIRA
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from mcp.server.fastmcp import FastMCP

load_dotenv()

mcp = FastMCP("ticket-triage-agent")

# ── CONNECTIONS ─────────────────────────────────────────────────────────────────

def get_jira_client():
    return JIRA(
        server=os.getenv("JIRA_URL"),
        basic_auth=(os.getenv("JIRA_EMAIL"), os.getenv("JIRA_API_TOKEN"))
    )

def get_slack_client():
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    return WebClient(
        token=os.getenv("SLACK_BOT_TOKEN"),
        ssl=ssl_context
    )

# ── MOCK DATA (team info stays local) ──────────────────────────────────────────

TEAM_ROUTING = {
    "technical_bug": "Technical Team",
    "business_request": "Payroll Team",
    "general_question": "Support Team"
}

TEAM_MEMBERS = {
    "Technical Team": [
        {"name": "Alice", "available_hours": 10, "clients": ["Acme Corp", "TechNova"]},
        {"name": "Bob", "available_hours": 3, "clients": ["BlueStar Inc"]},
        {"name": "Carlos", "available_hours": 8, "clients": []}
    ],
    "Payroll Team": [
        {"name": "Diana", "available_hours": 6, "clients": ["BlueStar Inc"]},
        {"name": "Eve", "available_hours": 2, "clients": ["Acme Corp"]}
    ],
    "Support Team": [
        {"name": "Frank", "available_hours": 12, "clients": ["Acme Corp", "BlueStar Inc"]},
        {"name": "Grace", "available_hours": 5, "clients": []}
    ]
}

# ── SKILLS ─────────────────────────────────────────────────────────────────────

@mcp.tool()
def get_ticket(ticket_id: str) -> str:
    """Fetch a real Jira ticket by its ID. Returns the summary, description, priority, status, and reporter."""
    try:
        jira = get_jira_client()
        issue = jira.issue(ticket_id)
        result = {
            "id": ticket_id,
            "summary": issue.fields.summary,
            "description": issue.fields.description or "No description provided",
            "priority": issue.fields.priority.name if issue.fields.priority else "Medium",
            "status": issue.fields.status.name,
            "reporter": issue.fields.reporter.displayName if issue.fields.reporter else "Unknown"
        }
        return json.dumps(result)
    except Exception as e:
        return f"Could not fetch ticket {ticket_id}. Error: {str(e)}"


@mcp.tool()
def get_team_for_category(category: str) -> str:
    """Given an issue category (technical_bug, business_request, or general_question), returns the responsible team name."""
    team = TEAM_ROUTING.get(category)
    if not team:
        return f"Unknown category '{category}'. Valid options are: {list(TEAM_ROUTING.keys())}"
    return team


@mcp.tool()
def get_team_members(team_name: str) -> str:
    """Returns all members of a given team along with their available hours and list of clients they have worked with before."""
    members = TEAM_MEMBERS.get(team_name)
    if not members:
        return f"No team found with name '{team_name}'. Valid teams are: {list(TEAM_MEMBERS.keys())}"
    return json.dumps(members)


@mcp.tool()
def recommend_assignee(team_name: str, client: str, severity: str) -> str:
    """Given a team, client name, and ticket severity, recommends the best assignee based on availability and client history."""
    members = TEAM_MEMBERS.get(team_name, [])
    if not members:
        return f"No team found: {team_name}"

    with_history = [m for m in members if client in m["clients"]]
    without_history = [m for m in members if client not in m["clients"]]

    available_with_history = [m for m in with_history if m["available_hours"] >= 4]
    available_without_history = [m for m in without_history if m["available_hours"] >= 4]

    if available_with_history:
        best = max(available_with_history, key=lambda m: m["available_hours"])
        return f"Recommend {best['name']} — has client history with {client} and {best['available_hours']} hours available."

    if severity in ["High", "Critical"]:
        if available_without_history:
            best = max(available_without_history, key=lambda m: m["available_hours"])
            return f"Recommend {best['name']} — no client history but {best['available_hours']} hours available. Severity is {severity} so assigning best available."
        anyone = max(members, key=lambda m: m["available_hours"])
        return f"Recommend {anyone['name']} — limited availability across team. Severity is {severity}, assigning person with most hours: {anyone['available_hours']}."

    if available_without_history:
        best = max(available_without_history, key=lambda m: m["available_hours"])
        return f"Recommend {best['name']} — no client history but {best['available_hours']} hours available."

    return "No suitable assignee found. All team members are at capacity."


@mcp.tool()
def send_slack_recommendation(ticket_id: str, recommended_assignee: str, reasoning: str) -> str:
    """Sends a triage recommendation to Slack for human review and approval. Call this after determining the recommended assignee."""
    try:
        client = get_slack_client()
        channel = os.getenv("SLACK_CHANNEL", "#general")
        message = f"""*Triage Recommendation for {ticket_id}*

*Recommended Assignee:* {recommended_assignee}
*Reasoning:* {reasoning}

Please review and reply *approved* in Claude to log this to Jira, or *rejected* to cancel."""

        client.chat_postMessage(channel=channel, text=message)
        return f"Recommendation sent to Slack channel {channel}. Waiting for human approval in Claude before writing to Jira."
    except SlackApiError as e:
        return f"Could not send Slack message. Error: {str(e)}"


@mcp.tool()
def add_triage_comment(ticket_id: str, recommended_assignee: str, reasoning: str) -> str:
    """Only call this after the human has explicitly approved the recommendation in Claude. Adds a comment to the Jira ticket documenting the recommended assignee and reasoning."""
    try:
        jira = get_jira_client()
        comment = f"""*Triage Recommendation (AI Agent)*

*Recommended Assignee:* {recommended_assignee}

*Reasoning:* {reasoning}

_This recommendation was reviewed and approved by a human before being logged._"""
        jira.add_comment(ticket_id, comment)
        return f"Comment added to {ticket_id} successfully. Ticket updated with triage recommendation for {recommended_assignee}."
    except Exception as e:
        return f"Could not add comment to {ticket_id}. Error: {str(e)}"


# ── RUN ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")