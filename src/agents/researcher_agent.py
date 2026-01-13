import json
import re
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from src.config import BASE_URL, API_KEY, MODEL_NAME
from src.state import State, LiteraturePlan, LiteratureSummary
from src.tools.arxiv_tool import search_arxiv, author_stats

def find_json_objects(s):
    """Finds all JSON objects in a string using json.JSONDecoder.raw_decode."""
    s = s.strip()
    json_objects = []
    decoder = json.JSONDecoder()
    idx = 0
    while idx < len(s):
        idx = s.find('{', idx)
        if idx == -1:
            break
        try:
            obj, end_idx = decoder.raw_decode(s[idx:])
            json_objects.append(obj)
            idx += end_idx
        except json.JSONDecodeError:
            idx += 1
    return json_objects

llm = ChatOpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
    model=MODEL_NAME,
    streaming=True
)

def call_research_planner(state: State):
    print("🧠 Calling Researcher Agent (Planner)...")
    planner_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a research planner. Extract keywords from the user's query (e.g. if user says 'transformer architectures', extract ['transformer', 'architectures']). Decide min_year (e.g. 2020), and whether to check author stats (true/false). Respond in JSON format: {{\"keywords\": [], \"min_year\": 0, \"need_author_stats\": true}}"),
        ("human", "User request: {query}")
    ])
    response = llm.invoke([HumanMessage(content=planner_prompt.format_messages(query=state["query"])[0].content)])
    try:
        content = response.content
        print(f"🔍 Planner LLM response: {content}")
        if isinstance(content, str):
            json_matches = find_json_objects(content)
            if json_matches:
                json_obj = json_matches[-1]
                print(f"🔍 Extracted JSON object: {json_obj}")
                plan = LiteraturePlan(**json_obj)
                print(f"✅ Parsed plan: {plan}")
            else:
                raise ValueError("No JSON found in response content")
        else:
            plan = LiteraturePlan(**content)
            print(f"✅ Parsed plan: {plan}")
        return {"plan": plan}
    except Exception as e:
        print("❌ Error parsing planner response:", e)
        print("Response was:", response)
        return {"plan": LiteraturePlan(keywords=["default"], min_year=2020, need_author_stats=False)}

def call_research_arxiv(state: State):
    print("🔍 Calling Researcher Agent (ArXiv)...")
    papers = search_arxiv(state["plan"].keywords, state["plan"].min_year)
    return {"papers": papers}

def call_research_author_stats(state: State):
    authors = []
    for paper in state["papers"]:
        authors.extend(paper.authors)
    print(f"🔍 Calling Researcher Agent (Author Stats) for {len(authors)} authors...")
    stats = author_stats(list(set(authors)))
    return {"author_stats": stats}

def call_research_writer(state: State):
    print("✍️ Calling Researcher Agent (Writer)...")
    papers = state.get("papers", [])
    stats = state.get("author_stats", [])
    history_context = "\n".join([f"{msg['role']}: {msg['content'][:100]}..." for msg in state.get("chat_history", [])[-2:]])
    
    writer_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a literature review writer. Summarize the papers and author stats. Consider the conversation history for context. Respond in JSON format: {{\"main_trends\": \"\", \"notable_papers\": [{{\"author\": \"\", \"year\": 0, \"title\": \"\", \"summary\": \"\"}}], \"open_questions\": \"\"}}"),
        ("human", "Previous context:\n{history}\n\nPapers: {papers}\nAuthor stats: {stats}\n\nWrite a comprehensive summary.")
    ])
    formatted_messages = writer_prompt.format_messages(
        history=history_context if history_context else "No previous context",
        papers=papers,
        stats=stats
    )
    response = llm.invoke(formatted_messages)
    try:
        content = response.content
        if isinstance(content, str):
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                json_str = match.group()
                summary_json = json.loads(json_str)
                summary = LiteratureSummary(**summary_json)
                print(f"✅ Parsed summary: {summary}")
            else:
                raise ValueError("No JSON found in writer response content")
        else:
            summary = LiteratureSummary(**content)
            print(f"✅ Parsed summary: {summary}")
        return {"summary": summary}
    except Exception as e:
        print("❌ Error parsing writer response:", e)
        print("Response was:", response)
        return {"summary": LiteratureSummary(main_trends="Error processing.", notable_papers=[], open_questions="")}