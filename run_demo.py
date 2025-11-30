import asyncio
from src.graph import graph

async def run_demo():
    queries = [
        "Recent advances in transformer architectures",
        "Explain how to use LangGraph for a simple workflow",
        "Write a Python function to calculate factorial and run it",
        "How do I plan a project timeline for a research paper?",
        "What are the key challenges in multi-agent systems?"
    ]

    for i, query in enumerate(queries):
        print(f"\n--- Running Query {i+1}: {query} ---")
        inputs = {
            "query": query,
            "chat_history": [],
            "user_profile": {}
        }
        print("🚀 Starting graph execution...")
        async for output in graph.astream(inputs):
            for key, value in output.items():
                print(f"--- Node '{key}' ---")
                print(value)
                print()
        print("--- End of Query ---\n")

if __name__ == "__main__":
    asyncio.run(run_demo())