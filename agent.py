import json

from openai import OpenAI
from openai.resources.responses import input_items

from config import OPEN_API_KEY, CHAT_MODEL, MAX_ITERATION, MAX_MEMORY_SIZE
from email_service import send_gmail
from rag import  search_rules_in_rag
from tools import TOOLS, ask_email_apporval

client = OpenAI(base_url='https://api.gapgpt.app/v1', api_key=OPEN_API_KEY)

AGENT_INSTRUCTIONS = """
You are a simple AI agent for a company.

Your responsibilities:
1. Answer the user in Persian.
2. Use search_company_rules when company rules are relevant.
3. Never invent company rules.
4. If the user asks to send an email, use send_email.
5. The application will ask the human for approval before email is actually sent.
6. After every tool result, decide whether another tool is needed or whether the task is complete.
7. If a tool fails, explain the problem or choose another reasonable path.
8. Keep answers clear and concise.

Important:
- A tool is not automatically required for every request.
- Company policy claims must be grounded in search_company_rules results.
- We don't have any extra application like Slack or Calendar. just a rules file.
"""
PLANNER_INSTRUCTIONS = """
Create a short high-level execution plan for an ai agent.

Rules:
- Write the plan in Persian.
- Do not solve the task.
- Do not reveal private chain-of-thought.
- Only list observable actions the agent may perform.
- Mention tool names when a tool will probably be needed.
- Keep the plan between 1 and 5 numbered steps.
- We don't have any extra application like Slack or Calendar. just a rules file.
"""

def create_plan(user_input, memory):
    planner_input = []
    for message in memory[-MAX_MEMORY_SIZE:]:
        planner_input.append(message)

    planner_input.append({
        "role": "user",
        "content": user_input
    })
    try:
        response = client.chat.completions.create(
                model=CHAT_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": PLANNER_INSTRUCTIONS
                    },
                    *planner_input
                ]
            )
        plan = response.choices[0].message.content.strip()
        return plan
    except Exception as e:
        return "خطا در برنامه ریزی" + str(e)


def run_agent(user_input, memory, rag_index):
    print("\n====== Agent Started ======\n")

    state = {
        "goal": user_input,
        "plan": create_plan(user_input, memory),
        "iteration": 0,
        "last_tool": None,
        "status": "running"
    }
    print("\n===== Agent Plan =====\n")
    print(state["plan"])

    # Load previous conversation history
    input_items = memory[-MAX_MEMORY_SIZE:].copy()

    # Add the current user message
    input_items.append({
        "role": "user",
        "content": user_input
    })

    runtime_instructions = (
            AGENT_INSTRUCTIONS
            + "\n\n"
            + "Current execution plan:\n"
            + state["plan"]
            + "\n\n"
            + ("Follow this plan as a guide"
               "If a tool result shows that a astep is unnessesary "
               "or another action is required, adapt the execution")
    )

    for iteration in range(1, MAX_ITERATION + 1):
        state["iteration"] = iteration

        print(
            "State:\n",
            json.dumps(state, ensure_ascii=False, indent=2)
        )
        try:
            response = client.chat.completions.create(
                model=CHAT_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": runtime_instructions
                    },
                    *input_items
                ],
                tools=TOOLS,
                tool_choice="auto"
            )
        except Exception as e:
            state["status"] = "llm_error"
            return "خطا در ارتباط با مدل " + str(e)

        message = response.choices[0].message

        # No tool call: the model has produced its final answer
        if not message.tool_calls:
            final_answer = message.content or ""

            state["status"] = "completed"

            # Save the current conversation to persistent memory
            memory.append({
                "role": "user",
                "content": user_input
            })

            memory.append({
                "role": "assistant",
                "content": final_answer
            })

            # Keep memory within the configured limit
            del memory[:-MAX_MEMORY_SIZE]

            print(
                "State:\n",
                json.dumps(state, ensure_ascii=False, indent=2)
            )

            print("\n====== Agent Stopped ======\n")

            return final_answer

        # Preserve the assistant message containing tool calls
        input_items.append(
            message.model_dump(exclude_none=True)
        )

        # Execute requested tools
        for item in message.tool_calls:
            tool_name = item.function.name
            state["last_tool"] = tool_name
            print("Tool Call:", tool_name)
            tool_result_dump = ""
            if tool_name == "search_company_rules":
                arguments = json.loads(item.function.arguments)
                user_query = arguments["query"]

                tool_results = search_rules_in_rag(
                    rag_index,
                    user_query
                )

                tool_result_dump = json.dumps(
                    [
                        doc.model_dump()
                        for doc in tool_results
                    ],
                    ensure_ascii=False

                )

                print("Tool Result:", tool_result_dump)

                # Return the tool result to the model
                input_items.append({
                    "role": "tool",
                    "tool_call_id": item.id,
                    "content": tool_result_dump
                })
            elif tool_name == "send_email":
                arguments = json.loads(item.function.arguments)
                to = arguments["to"]
                subject = arguments["subject"]
                content = arguments["body"]
                approved=ask_email_apporval(to,subject,content)
                if not approved:
                    return json.dumps({
                        "status": "canceled_by_human",
                        "message": "The user did not approve sending the email."
                    })

                mail_results = send_gmail(to,subject,content)
                tool_result_dump = json.dumps(mail_results,ensure_ascii=False)
                print("Tool Result:", tool_result_dump)

                # Return the tool result to the model
                input_items.append({
                    "role": "tool",
                    "tool_call_id": item.id,
                    "content": tool_result_dump
                })

            else:
                input_items.append({
                    "role": "tool",
                    "tool_call_id": item.id,
                    "content": json.dumps({
                        "error": f"Unknown tool: {tool_name}"
                    })
                })

    state["status"] = "max_iterations_reached"

    print(
        "State:\n",
        json.dumps(state, ensure_ascii=False, indent=2)
    )

    print("\n====== Agent Stopped ======\n")

    return "Max Iterations Reached."
# ChatCompletion(id='gen-1793169179-7OqeT2cHRka1ldLQkklB', choices=[Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content='سلام! چطور می\u200cتونم کمکتون کنم؟', refusal=None, role='assistant', annotations=None, audio=None, function_call=None, tool_calls=None, reasoning=None), native_finish_reason='stop')], created=1793169179, model='openai/gpt-4o', object='chat.completion', metadata=None, moderation=None, service_tier='default', system_fingerprint='fp_4c910a9acf', usage=CompletionUsage(completion_tokens=13, prompt_tokens=24, total_tokens=37, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=None, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=None, text_tokens=None, image_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cache_write_tokens=0, cached_tokens=0, image_tokens=None, text_tokens=None, video_tokens=0), cost=0.00019, is_byok=False, cost_details={'upstream_inference_cost': 0.00019, 'upstream_inference_prompt_cost': 6e-05, 'upstream_inference_completions_cost': 0.00013}), provider='OpenAI')
