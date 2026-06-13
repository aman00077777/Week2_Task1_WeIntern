# CodePulse AI – Interactive Coding & Developer Assistant

CodePulse is a premium, responsive AI Chatbot designed to help developers learn coding concepts, write database queries, utilize version control, debug errors, and prepare for software engineering interviews. 

It is powered by a local Natural Language Processing (NLP) classifier built on top of `scikit-learn` (using TF-IDF feature extraction and Logistic Regression classification, combined with Cosine Similarity and Out-of-Vocabulary (OOV) checks for maximum classification accuracy).

---

## Features

1. **Dual Interfaces**: 
   - **Premium Emerald Glassmorphic Web App**: A dark-theme, blur-filtered UI with code-syntax highlighting, dynamic typing bubbles, active context stats, session logs, and a downloadable transcript feature.
   - **CLI Console Application**: A direct interactive shell within your terminal window.
2. **11 Supported Intents**: Custom training dataset spanning greetings, coding help, specific technologies, multi-turn code samples, and elaborate explanations.
3. **Context-Aware Multi-Turn Support**: Remembers conversational states (e.g., asking for "Python Basics" and then "give me an example" triggers a Python code block; asking for "Git Basics" followed by "give me an example" shows Git terminal instructions).
4. **Out-of-Vocabulary (OOV) Fallback Engine**: If a user enters off-topic content (e.g., "how do I bake cookies"), the model computes the percentage of unrecognized words and redirects to a friendly fallback assistant prompt.
5. **Zero-Bytecode Flag Configured**: Environment checks clean up and bypass creating `__pycache__` folders.

---

## Recommended System Setup

### Prerequisites
- Python 3.8 or above installed on Windows/Mac/Linux.

### Setup Instructions

1. **Initialize Python Virtual Environment**:
   ```powershell
   python -m venv .venv
   ```

2. **Install Dependencies**:
   ```powershell
   .venv\Scripts\pip install -r requirements.txt
   ```

---

## Running the Chatbot

### Interface 1: Premium Web Dashboard
To launch the Web app:
```powershell
# Set environment to prevent python bytecode caching
$env:PYTHONDONTWRITEBYTECODE=1
python app.py
```
Open your browser and navigate to: **`http://127.0.0.1:5000`**

### Interface 2: Interactive Terminal (CLI)
To run directly in your console:
```powershell
python chatbot.py
```

---

## Running the Automated Test Suite

We have provided a comprehensive verification script containing 22 diverse test queries (greetings, technology questions, context switches, follow-up examples, gibberish, and off-topic fallbacks). 

To execute the test table:
```powershell
python test_chatbot.py
```

---

## Supported Intents and Triggers Reference

| Intent Tag | Context Set | Sample Utterances / Triggers | Chatbot Topic Response |
| :--- | :--- | :--- | :--- |
| `greeting` | None | "hello", "hi", "yo", "good morning" | Conversational chatbot introduction |
| `goodbye` | Clears Context | "bye", "see you later", "exit", "quit" | Closing remarks |
| `bot_identity` | None | "who are you", "what is your name" | Explains CodePulse's features & identity |
| `help` | None | "help", "what can you do", "features" | Displays the help directory |
| `python_basics` | `python_context` | "explain python", "learn python" | High-level overview of Python features |
| `git_basics` | `git_context` | "how to use git", "git commands" | Version control commands and structure |
| `api_basics` | `api_context` | "what is an api", "explain rest api" | REST architectural style and HTTP methods |
| `sql_queries` | `sql_context` | "what is sql", "database query select" | Structured Query Language overview |
| `frontend_vs_backend` | `webdev_context`| "frontend vs backend", "client vs server"| Frontend rendering vs backend databases |
| `debug_code` | `debug_context` | "fix my code", "syntax error debug" | Step-by-step developer debugging guide |
| `interview_tips` | `interview_context`| "prep for coding interview", "leetcode prep"| Data structures, algorithms, and prep resources |
| `context_example` | None | "give me an example", "code sample" | *Dynamic*: Returns code code-block for the active context |
| `context_more` | None | "tell me more", "explain further" | *Dynamic*: Elaborates in-depth details for the active context |