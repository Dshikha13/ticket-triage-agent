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
-
