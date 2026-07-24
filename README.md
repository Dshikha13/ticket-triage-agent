# Ticket Triage Agent
An AI agent that autonomously triages incoming support tickets using the Model Context Protocol (MCP), with Slack notification and human-in-the-loop approval before writing to Jira.
---

## Why I Built This

Throughout my experience, I noticed that support ticket triage was always a manual process. Someone had to read every incoming ticket, figure out what kind of issue it was, identify the right team, check who had bandwidth, see if anyone had worked with that client before, weigh the severity, and then assign it. That process took 10 to 15 minutes every single time, for every ticket.

I built this agent to automate that investigation work while keeping a human in control of the final decision.

---

## What It Does

1. Reads a real Jira ticket and extracts the issue details
2. Classifies the issue type (technical bug, business request, or general question)
3. Routes to the responsible team based on category
4. Evaluates team member availability and client history
5. Applies severity-based logic to recommend the best assignee
6. Sends the recommendation to Slack for human review
7. Only writes to Jira after explicit human approval

The agent does the investigation. The human makes the final call. Nothing is written to Jira without approval.

---

## The Human-in-the-Loop Design

This was a deliberate design decision, not a limitation.

In a real support environment, an automated system that assigns tickets without review creates risk — wrong assignments, missed context, frustrated clients. By keeping a human in the approval loop, the agent handles the time-consuming investigation work (which it does in seconds) while the human retains control over the actual assignment decision (which takes them 10 seconds to review and approve).

A production deployment would replace the current chat-based approval with a Slack button workflow, scoped as v2.

---

## Tech Stack

- Python
- MCP (Model Context Protocol) via FastMCP
- Jira API (real ticket read and write)
- Slack SDK (recommendation notifications)
- Claude Desktop (agent runtime)
- dotenv (secure credential management)

---

## Skills (MCP Tools)

|    Skill     |    Type     |    What it does    |
|---|---|---|
| get_ticket | Read, deterministic | Fetches real Jira ticket details |
| get_team_for_category | Read, deterministic | Maps issue category to responsible team |
| get_team_members | Read, deterministic | Returns team members with availability and client history |
| recommend_assignee | Read, logic-based | Applies severity rules to recommend best assignee |
| send_slack_recommendation | Write, low risk | Sends recommendation to Slack for human review |
| add_triage_comment | Write, gated | Posts to Jira only after human approval |

---

## What I Learned

- Deterministic skills should handle structured lookups. LLM reasoning should be reserved for unstructured judgment calls. Mixing them up makes agents slow and unpredictable.
- Skill descriptions are prompts for the agent, not documentation for humans. A vague description means the agent will not know when to use the skill.
- The human-in-the-loop gate is the most important design decision in this project. It is what separates a useful tool from a risky one.

---

## What is Next (v2)

- Slack button-based approval so the human can approve directly in Slack without switching to Claude
- Webhook listener that captures the approval and writes to Jira automatically with the approver's name
- Real team capacity pulled from Jira instead of mock data

---

## Setup

1. Clone the repo
2. Run `uv install` to install dependencies
3. Create a `.env` file with your credentials (see `.env.example`)
4. Connect to Claude Desktop via MCP config
5. Ask Claude to triage any Jira ticket by ID

---

*Built by Deepshikha Singh*  
*This project is licensed under the MIT License*
