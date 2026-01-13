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

def call_reviewer(state: State):
    print("🔍 Calling Reviewer Agent...")
    
    review_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Quality Reviewer Agent. Review the assistant's response for:\n"
                   "1. Completeness - does it answer the user's query?\n"
                   "2. Accuracy - are there any obvious errors?\n"
                   "3. Clarity - is it well-structured and easy to understand?\n"
                   "4. Relevance - does it stay on topic?\n\n"
                   "Respond with:\n"
                   "- 'approved' if the response is good quality\n"
                   "- 'needs_revision' if there are issues that should be addressed\n"
                   "Then provide brief feedback (1-2 sentences) explaining your decision."),
        ("human", "User query: {query}\n\nAssistant response: {response}\n\nReview the response quality.")
    ])
    
    response_text = ""
    if state.get("summary"):
        summary = state["summary"]
        response_text = f"Main trends: {summary.main_trends}\n\n"
        response_text += "Notable papers:\n"
        for paper in summary.notable_papers:
            response_text += f"- {paper.title} ({paper.year}) by {paper.author}: {paper.summary}\n"
        response_text += f"\nOpen questions: {summary.open_questions}"
    elif state.get("code_response"):
        response_text = state["code_response"]
    
    formatted_messages = review_prompt.format_messages(
        query=state["query"],
        response=response_text
    )
    review_response = llm.invoke(formatted_messages)
    review_content = review_response.content.strip().lower()
    
    approved = "approved" in review_content
    feedback = review_response.content
    
    print(f"✅ Reviewer decision: {'APPROVED' if approved else 'NEEDS_REVISION'}")
    print(f"📝 Reviewer feedback: {feedback[:100]}...")
    
    updated_history = state.get("chat_history", [])
    if approved:
        final_answer = response_text
        updated_history.append({"role": "assistant", "content": final_answer})
    else:
        final_answer = f"{response_text}\n\n[Reviewer Note: {feedback}]"
        updated_history.append({"role": "assistant", "content": final_answer})
    
    return {
        "reviewer_feedback": feedback,
        "final_answer": final_answer,
        "chat_history": updated_history
    }
