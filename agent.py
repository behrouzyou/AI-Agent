import json

from openai import OpenAI
from openai.resources.responses import input_items

from config import OPEN_API_KEY, CHAT_MODEL,MAX_ITERATION
from rag import  search_rules_in_rag
from tools import TOOLS

client = OpenAI(base_url='https://api.gapgpt.app/v1', api_key=OPEN_API_KEY)

AGENT_INSTRUCTIONS = """
You are a company assistant.
Always answer in Persian.
"""

def run_agent(user_input,rag_index):
    print("\n====== Agent Started ======\n")
    state = {
        "goal":user_input,
        "iteration": 0,
        "last_tool":None,
        "status": "running"
    }
    input_items = []
    for iteration in range(1, MAX_ITERATION + 1):
        state["iteration"]= iteration
        print("State: \n", json.dumps(state, ensure_ascii=False, indent=2))
        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": AGENT_INSTRUCTIONS},
                {"role": "user", "content": user_input}
            ],
             tools=TOOLS,
            tool_choice="auto"

        )




        message = response.choices[0].message
        input_items.extend(message)
        function_calls = []

        if message.tool_calls:
            for item in message.tool_calls:

                function_calls.append(item)

            if len(function_calls) == 0:
                final_answer = response.output_text.strip()
                state["status"] = "completed"
                print("State: \n", json.dumps(state, ensure_ascii=False, indent=2))
                return final_answer
            for item in function_calls:
                tool_name = item.function.name
                state["last_tool"] = tool_name
                print("Tool Call: ", tool_name)
                if tool_name == "search_company_rules":
                    arguments = json.loads(item.function.arguments)
                    user_query = arguments["query"]

                    tool_results = search_rules_in_rag(
                        rag_index,
                        user_query
                    )
                    tool_result_dump = json.dumps(
                        [doc.model_dump() for doc in tool_results],
                        ensure_ascii=False
                    )
                    print("Tool Result: ", tool_result_dump)


                    input_items.append({
                        "role": "tool",
                        "tool_call_id": item.id,
                        "output": tool_result_dump
                    })

    state["status"] = "max_iterations_reached"
    print("State: \n", json.dumps(state, ensure_ascii=False, indent=2))
    return ("\n====== Agent Stopped ======\n"
            "Max Iterations Reached.")

# ChatCompletion(id='gen-1793169179-7OqeT2cHRka1ldLQkklB', choices=[Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content='سلام! چطور می\u200cتونم کمکتون کنم؟', refusal=None, role='assistant', annotations=None, audio=None, function_call=None, tool_calls=None, reasoning=None), native_finish_reason='stop')], created=1793169179, model='openai/gpt-4o', object='chat.completion', metadata=None, moderation=None, service_tier='default', system_fingerprint='fp_4c910a9acf', usage=CompletionUsage(completion_tokens=13, prompt_tokens=24, total_tokens=37, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=None, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=None, text_tokens=None, image_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cache_write_tokens=0, cached_tokens=0, image_tokens=None, text_tokens=None, video_tokens=0), cost=0.00019, is_byok=False, cost_details={'upstream_inference_cost': 0.00019, 'upstream_inference_prompt_cost': 6e-05, 'upstream_inference_completions_cost': 0.00013}), provider='OpenAI')
