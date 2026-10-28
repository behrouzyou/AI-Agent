from agent import run_agent
from config import TOP_K
from rag import prepare_rag
from rag_steps.retrieval import retrieve

rag_index = prepare_rag()

user_input = input("شما:")
memory = []

answer = run_agent(user_input,memory,rag_index)


print("\nپاسخ:")
print(answer)
print("=========================MEMORY============================")
for mem in memory:
    print(mem)