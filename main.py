from agent import run_agent
from config import TOP_K
from rag import prepare_rag
from rag_steps.retrieval import retrieve

rag_index = prepare_rag()

user_input = input("شما:")

answer = run_agent(user_input,rag_index)

print("\nپاسخ:")
print(answer)