from dotenv import load_dotenv
from agent.pipeline import run_pipeline

load_dotenv()

def chat():
    while True:
        user_input = input("Вы: ").strip()
        if not user_input or user_input.lower() == "exit":
            break
        response = run_pipeline(user_input)
        print(f"ассистент {response}")

if __name__ == "__main__":
    chat()