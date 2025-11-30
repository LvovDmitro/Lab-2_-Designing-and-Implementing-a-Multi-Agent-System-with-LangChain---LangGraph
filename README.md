# Multi-Agent Study & Productivity Assistant

This project implements a Multi-Agent System (MAS) using LangChain and LangGraph. It serves as a study and productivity assistant, capable of handling research queries, coding questions, and more by routing them to specialized agents.

## Features

*   **Multi-Agent Architecture**: Uses Router, Researcher, and CodeHelper agents.
*   **LangGraph Orchestration**: Manages agent interactions and state.
*   **Tool Calling**: Uses an `arxiv` search tool for research tasks.
*   **Memory Management**: Maintains a simple chat history within a session.
*   **Reusable Components**: Code is structured into separate modules for agents, tools, and state.

## Setup

1.  **Clone the Repository** (or download the folder structure).
2.  **Create a Virtual Environment** (recommended to isolate dependencies):
    *   Open your terminal/command prompt in the project directory.
    *   Run: `python -m venv venv`
    *   Activate it:
        *   On Windows: `venv\Scripts\activate`
        *   On macOS/Linux: `source venv/bin/activate`
3.  **Install Dependencies**: Run `pip install -r requirements.txt`.
4.  **Environment Variables**: Create a `.env` file in the project root (same level as `run_demo.py`) with the following content:
    ```env
    LITELLM_BASE_URL=http://a6k2.dgx:34000/v1
    LITELLM_API_KEY=
    MODEL_NAME=qwen3-32b
    ```
    Replace the values with your actual vLLM endpoint details if they differ.

## Architecture

### Agents

*   **Router Agent**: Classifies the user query into categories like 'research', 'coding', 'planning', 'other'. *Note: Current implementation often returns 'other' but routes correctly based on conditional logic.*
*   **Researcher Agent**: Handles research tasks. It includes sub-steps: Planner (creates a search plan based on the query), ArXiv (executes search using the plan), Author Stats (fetches stats if needed), and Writer (summarizes results).
*   **CodeHelper Agent**: Provides assistance with coding-related queries and general questions.

### MAS Pattern

The system implements a **Router + Specialists** pattern. The Router Agent decides which specialist agent (Researcher or CodeHelper) should handle the request based on its classification.

### Diagram

```mermaid
graph TD
    A[User Query] --> B(Router Agent)
    B -->|research| C(Researcher Agent)
    B -->|coding/planning/other| D(CodeHelper Agent)
    C --> E(Memory/State)
    D --> E
    E --> F(Final Answer)