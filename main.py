from agent import run_agent

from rag import prepare_rag

def main():
    print("Preparing Rag...")
    rag_index = prepare_rag()
    print("Agent is ready")
    print("برای خروج exit را وارد کنید.")
    print("===============================")
    memory = []
    while True:

        user_input = input("شما:")
        user_input = user_input.strip()
        if user_input == "exit":
            print("پایان برنامه")
            break

        if user_input == "":
            continue

        answer = run_agent(user_input,memory,rag_index)
        print("\nپاسخ:")
        print(answer)
        print("=====================================================")


if __name__ == "__main__":
    main()
