from flask import Flask, request
import json

from llm_reply import generate_reply, send_email
from backend import perform_backend_action, current_time
from database import (
    get_email_log,
    add_email_log,
    add_message,
)

app = Flask(__name__)


@app.route("/email", methods=["POST"])
def receive_email():

    try:

        data = request.get_json()

        customer_email = data["envelope"]["from"]
        customer_subject = data["headers"]["subject"]
        customer_message = data["plain"]

        print("=" * 60)
        print("New Customer Email")
        print("=" * 60)

        print(f"From    : {customer_email}")
        print(f"Subject : {customer_subject}")
        print(f"Message :\n{customer_message}")

        mail = {
            "from": customer_email,
            "subject": customer_subject,
            "body": customer_message
        }

        headers = data.get("headers", {})

        message_id = (
            headers.get("message_id")
            or headers.get("message-id")
            or headers.get("Message-ID")
        )
        headers = data.get("headers", {})
        

        if message_id and get_email_log(message_id):
            print("Duplicate email received. Ignoring.")
            return "Already Processed", 200

        result = generate_reply(mail)

        if result is None:
            return "Generation Failed", 500

        if result.get("backend_action") != "NONE":
            perform_backend_action(
                result["backend_action"],
                result["order"],
                result["parameters"]
            )

        send_email(
            mail["from"],
            result["subject"],
            result["reply"]
        )

        add_message(
            result["order_id"],
            {
                "message_id": message_id,
                "direction": "incoming",
                "channel": "Email",
                "subject": result["subject"],
                "body": result["reply"],
                "timestamp": current_time()
            }
        )

        add_email_log(
            {
                "message_id": message_id,
                "customer_email": customer_email,
                "order_id": result["order"]["order_id"],
                "backend_action": result["backend_action"],
                "processed_at": current_time(),
                "status": "Processed"
            }
        )
        return "OK", 200

    except Exception as e:

        print(f"Server Error: {e}")
        return "Internal Server Error", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)