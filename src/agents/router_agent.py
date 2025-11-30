from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from src.config import BASE_URL, API_KEY, MODEL_NAME
from src.state import State
import re

llm = ChatOpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
    model=MODEL_NAME,
    streaming=True
)

def call_router(state: State):
    print("🧠 Calling Router Agent...")
    # Более конкретный промпт с инструкцией строго выбрать одну категорию
    router_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Router Agent. Classify the user's query into one of the following categories: 'research', 'coding', 'planning', 'other'. Respond with ONLY the category name, nothing else. Do not add explanations or punctuation."),
        ("human", "User query: {query}")
    ])
    response = llm.invoke([HumanMessage(content=router_prompt.format_messages(query=state["query"])[0].content)])
    raw_category = response.content.strip().lower()
    print(f"🤖 Raw Router response: {raw_category}")
    
    # Более устойчивое сопоставление ответа
    if 'research' in raw_category:
        category = 'research'
    elif 'coding' in raw_category or 'code' in raw_category or 'python' in raw_category:
        category = 'coding'
    elif 'planning' in raw_category or 'timeline' in raw_category or 'plan' in raw_category:
        category = 'planning'
    else:
        # Попробуем найти любое совпадение с ключевыми словами
        if any(word in raw_category for word in ['other', 'general', 'question', 'help']):
            category = 'other'
        else:
            # Если не понятно, всё равно отправим в 'coding' как более общий путь для неопределённых запросов
            # или в 'research' как основной путь из первой лабы.
            # Лучше настроить на 'other' или 'research' в зависимости от целей.
            # Пусть будет 'research', так как это был основной сценарий.
             print(f"⚠️ Router could not classify '{raw_category}', defaulting to 'research'.")
             category = 'research'

    # Явно проверим, попал ли ответ в нужные категории после сопоставления
    if category not in ['research', 'coding', 'planning', 'other']:
        print(f"⚠️ Router returned invalid category '{category}', defaulting to 'research'.")
        category = 'research'

    print(f"🏷️ Router classified query as: {category}")
    # Update history
    new_message = {"role": "user", "content": state["query"]}
    updated_history = state.get("chat_history", []) + [new_message]
    return {"category": category, "chat_history": updated_history}