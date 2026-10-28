
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_company_rules",
            "description": (
                "Search the company's internal rules "
                "using RAG."
            ),
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "A focused query for "
                            "searching company rules."
                        )
                    }
                },
                "required": ["query"],
                "additionalProperties": False
            }
        }
    },
{
        "type": "function",
        "function": {
            "name": "send_email",
            "description": (
                "Sends an email through the configured Gmail account."
                "This tool has an external side effect and must always "
                "require human approval before the email is sent."
            ),
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "Recipient email address."
                    },
                    "subject": {
                    "type": "string",
                    "description": "Subject of the email."
                },
                     "body": {
                    "type": "string",
                    "description": "Body of the email."
                }
                },
                "required":["to", "subject", "body"],
                "additionalProperties": False
            }
        }
    }
]

def ask_email_apporval(to, subject, body):
    print("Asking email apporval...")
    print("To: ", to)
    print("Subject: ", subject)
    print("Body: ", body)
    print("\n")
    answer = input("آیا این ایمیل ارسال شود؟ (yes/no)")

    answer = answer.lower().strip()
    if answer == "yes":
        return True
    return False