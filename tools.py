
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
    }
]
