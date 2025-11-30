from langgraph.graph import StateGraph, END
from src.state import State
from src.agents.router_agent import call_router
from src.agents.researcher_agent import call_research_planner, call_research_arxiv, call_research_author_stats, call_research_writer
from src.agents.code_helper_agent import call_code_helper

def route_after_router(state):
    category = state["category"]
    print(f"🔄 Routing based on category: {category}")
    if category == "research":
        return "research_planner"
    # Теперь явно указываем, что все остальные категории идут к code_helper
    elif category in ["coding", "planning", "other"]:
        return "code_helper"
    else:
        # На всякий случай, если category не распознана
        print(f"⚠️ Unknown category '{category}', routing to 'code_helper'.")
        return "code_helper"

def route_after_arxiv(state):
    if state["plan"].need_author_stats:
        return "research_author_stats"
    else:
        return "research_writer"

def build_graph():
    graph_builder = StateGraph(State)

    graph_builder.add_node("router", call_router)
    graph_builder.add_node("research_planner", call_research_planner)
    graph_builder.add_node("research_arxiv", call_research_arxiv)
    graph_builder.add_node("research_author_stats", call_research_author_stats)
    graph_builder.add_node("research_writer", call_research_writer)
    graph_builder.add_node("code_helper", call_code_helper)

    graph_builder.add_edge("router", "research_planner")
    graph_builder.add_edge("research_planner", "research_arxiv")
    graph_builder.add_conditional_edges("research_arxiv", route_after_arxiv, ["research_author_stats", "research_writer"])
    graph_builder.add_edge("research_author_stats", "research_writer")
    graph_builder.add_edge("research_writer", END)
    # Добавляем маршрутизацию после роутера к code_helper
    graph_builder.add_conditional_edges("router", route_after_router, ["research_planner", "code_helper"])
    # Убираем прямое ребро от router к research_planner, так как теперь оно через conditional_edges
    # graph_builder.add_edge("router", "research_planner") # <-- УДАЛИТЬ ЭТУ СТРОКУ
    # Убираем также лишнее добавление ребра к code_helper, если оно было после conditional_edges
    # graph_builder.add_edge("router", "code_helper") # <-- УДАЛИТЬ, ЕСЛИ ЕСТЬ
    graph_builder.add_edge("code_helper", END)

    # Удаляем старое определение точки входа и добавляем новое
    # graph_builder.set_entry_point("router") # <-- Должно быть в конце, после всех рёбер
    # Убираем лишнее ребро от research_writer к code_helper, если оно случайно добавилось
    # graph_builder.add_edge("research_writer", "code_helper") # <-- УДАЛИТЬ, ЕСЛИ ЕСТЬ

    graph_builder.set_entry_point("router")

    return graph_builder.compile()

graph = build_graph()