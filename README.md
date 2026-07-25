# Ticket Triage Agent

An AI agent that autonomously triages incoming support tickets using the Model Context Protocol (MCP), with Slack notification and human-in-the-loop approval before writing to Jira.

Built by Deepshikha Singh

---

## Why I Built This

Across my experience in enterprise SaaS consulting, I noticed that support ticket triage was always a manual process. Someone had to read every incoming ticket, figure out what kind of issue it was, identify the right team, check who had bandwidth, see if anyone had worked with that client before, weigh the severity, and then assign it. That process took 10 to 15 minutes every single time, for every ticket.

I built this agent to automate that investigation work while keeping a human in control of the final decision.

---

## How It Works

1. A new support ticket comes in on Jira
2. The agent reads the ticket and classifies the issue type
3. It identifies the responsible team based on category
4. It evaluates team member availability and client history
5. It applies severity based logic to recommend the best assignee
6. It sends the recommendation to Slack for human review
7. The human types "approved" in Slack
8. The agent writes a comment to the Jira ticket with the assignee, reasoning, and approver name

The agent does the investigation. The human makes the final call. Nothing is written to Jira without approval.

---

## The Human-in-the-Loop Design

This was a deliberate design decision, not a limitation.

In a real support environment, an automated system that assigns tickets without review creates risk. Wrong assignments, missed context, frustrated clients. By keeping a human in the approval loop, the agent handles the time-consuming investigation work in seconds while the human retains control over the actual assignment decision.

The approval happens directly in Slack. The approver's real name is captured automatically and written to the Jira comment for full audit trail.

---

## Tech Stack

- Python
- MCP (Model Context Protocol) via FastMCP
- Jira API (real ticket read and write)
- Slack SDK (recommendation notifications and approval capture)
- ngrok (webhook tunneling for local development)
- Claude Desktop (agent runtime for v1)
- Anthropic API (programmatic agent calls for v2)
- dotenv (secure credential management)

---

## Skills (MCP Tools)

| Skill | Type | What it does |
|---|---|---|
| get_ticket | Read, deterministic | Fetches real Jira ticket details |
| get_team_for_category | Read, deterministic | Maps issue category to responsible team |
| get_team_members | Read, deterministic | Returns team members with availability and client history |
| recommend_assignee | Read, logic based | Applies severity rules to recommend best assignee |
| send_slack_recommendation | Write, low risk | Sends recommendation to Slack for human review |
| add_triage_comment | Write, gated | Posts to Jira only after human approval |

---

## What I Learned

Deterministic skills should handle structured lookups. LLM reasoning should be reserved for unstructured judgment calls. Mixing them up makes agents slow and unpredictable.

Skill descriptions are prompts for the agent, not documentation for humans. A vague description means the agent will not know when to use the skill.

The human-in-the-loop gate is the most important design decision in this project. It is what separates a useful tool from a risky one.

Two separate Python processes cannot share memory. Pending approvals need to be persisted to a shared file or database so the webhook server can read what the MCP server wrote.

---

## Roadmap

**v1 (shipped):** MCP agent reads real Jira tickets, applies triage logic, sends Slack notification, posts to Jira after human approval in Claude Desktop

**v2 (shipped):** Slack webhook approval flow. Human types "approved" in Slack channel. Approver name captured automatically and written to Jira comment. No Claude Desktop required for approval step.

**v3 (planned):** Jira webhook triggers triage automatically when a new ticket is created. Full end to end automation with zero manual steps. Team availability pulled from live data source instead of structured mock data.

---

## Setup

1. Clone the repo
2. Run `uv install` to install dependencies
3. Create a `.env` file with your credentials (see below)
4. Start the webhook server with `uv run python webhook_server.py`
5. Start ngrok with `ngrok http 5000`
6. Connect to Claude Desktop via MCP config
7. Ask Claude to triage any Jira ticket by ID

### Required environment variables

JIRA_URL=https://yoursite.atlassian.net
JIRA_EMAIL=your@email.com
JIRA_API_TOKEN=your_jira_token
JIRA_PROJECT_KEY=YOUR_KEY
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_CHANNEL=#your-channel

---

*MIT License*
