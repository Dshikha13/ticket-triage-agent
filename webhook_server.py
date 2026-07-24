import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv
from jira import JIRA
from slack_sdk import WebClient

load_dotenv()

PENDING_FILE = "/tmp/pending_approvals.json"

def load_pending():
    try:
        with open(PENDING_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_pending(data):
    with open(PENDING_FILE, "w") as f:
        json.dump(data, f)

def store_pending_approval(ticket_id, assignee, reasoning):
    data = load_pending()
    data[ticket_id] = {
        "assignee": assignee,
        "reasoning": reasoning
    }
    save_pending(data)
    print(f"Stored pending approval for {ticket_id}")

def get_jira_client():
    return JIRA(
        server=os.getenv("JIRA_URL"),
        basic_auth=(os.getenv("JIRA_EMAIL"), os.getenv("JIRA_API_TOKEN"))
    )

def get_user_name(user_id):
    try:
        client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
        response = client.users_info(user=user_id)
        name = response["user"]["real_name"]
        print(f"Resolved name: {name}")
        return name
    except Exception as e:
        print(f"Name lookup failed: {e}")
        return user_id

class WebhookHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body)
        except Exception as e:
            print(f"JSON parse error: {e}")
            self.send_response(200)
            self.end_headers()
            return

        # Slack verification challenge
        if "challenge" in data:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"challenge": data["challenge"]}).encode())
            return

        # Log everything we receive
        event = data.get("event", {})
        event_type = event.get("type")
        bot_id = event.get("bot_id")
        text = event.get("text", "").strip()
        user_id = event.get("user", "unknown")
        print(f"Event: type={event_type} bot_id={bot_id} text={text} user={user_id}")

        # Only process real user messages
        if event_type == "message" and bot_id is None and text.lower() == "approved":
            user_name = get_user_name(user_id)
            pending = load_pending()

            if pending:
                ticket_id, approval_data = list(pending.items())[-1]
                try:
                    jira = get_jira_client()
                    comment = f"""*Triage Recommendation (AI Agent)*

*Recommended Assignee:* {approval_data['assignee']}

*Reasoning:* {approval_data['reasoning']}

*Approved by:* {user_name} via Slack

_This recommendation was reviewed and approved by a human before being logged._"""
                    jira.add_comment(ticket_id, comment)
                    print(f"Comment added to {ticket_id} approved by {user_name}")

                    updated = load_pending()
                    if ticket_id in updated:
                        del updated[ticket_id]
                    save_pending(updated)

                except Exception as e:
                    print(f"Jira error: {e}")
            else:
                print("No pending approvals found")

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        print(f"Webhook: {format % args}")


if __name__ == "__main__":
    port = 5000
    server = HTTPServer(("0.0.0.0", port), WebhookHandler)
    print(f"Webhook server running on port {port}")
    server.serve_forever()