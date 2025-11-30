from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from src.config import BASE_URL, API_KEY, MODEL_NAME
from src.state import State

llm = ChatOpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
    model=MODEL_NAME,
    streaming=True
)

def call_code_helper(state: State):
    print("💻 Calling CodeHelper Agent...")
    # Include history in the prompt for context
    history_context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in state.get("chat_history", [])[-3:]]) # Last 3 messages
    prompt_with_history = f"Context:\n{history_context}\n\nUser query: {state['query']}\n\nProvide code assistance. Be concise."
    response = llm.invoke([HumanMessage(content=prompt_with_history)])
    code_response = response.content
    print(f"💻 CodeHelper response: {code_response}")
    # Update history
    new_message = {"role": "assistant", "content": code_response}
    updated_history = state.get("chat_history", []) + [new_message]
    return {"code_response": code_response, "chat_history": updated_history}