"""
(NAYA) Data Isolation (Level 3.2 & 4.2)
Saara dummy data, conversational history, aur 1-to-1 mapped 
ground truth arrays yahan rahenge taaki test files clean rahein.
"""
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

# 1. QUESTIONS ARRAY (10 Items: 4 HTML, 3 JS, 3 MySQL)
QUESTIONS = [
    "How do you define a block quotation of text in HTML?",
    "What is the semantic tag for sidebar content?",
    "How do you create an email link in HTML?",
    "What is the meta tag for responsive design?",
    "How do you pause execution in DevTools?",
    "How do you declare a block-scoped variable that cannot be reassigned?",
    "How do you add a new element to the end of an array in JavaScript?",
    "How do you list all databases in MySQL?",
    "How do you ensure a column disallows NULL values in MySQL?",
    "What command undoes transaction changes in MySQL?"
]

# 2. GROUND TRUTH ANSWERS (Mapped 1:1 to QUESTIONS)
GROUND_TRUTH_ANSWERS = [
    "<blockquote>A block quotation of text</blockquote>", #[cite: 1]
    "<aside>Sidebar content</aside>", #[cite: 1]
    "<a href=\"mailto:example@email.com\">Send Email</a>", #[cite: 1]
    "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">", #[cite: 1]
    "debugger // Pauses execution in DevTools", #[cite: 3]
    "const PI=3.14 // Block-scoped, cannot be reassigned", #[cite: 3]
    "arr.push (4);", #[cite: 3]
    "SHOW DATABASES;", #[cite: 2]
    "NOT NULL", #[cite: 2]
    "ROLLBACK" #[cite: 2]
]

# 3. QUESTION TO TOOL MAPPING
QUESTION_TOOL_MAP = {
    "How do you define a block quotation of text in HTML?": "check_html_syntax",
    "What is the semantic tag for sidebar content?": "check_html_syntax",
    "How do you create an email link in HTML?": "check_html_syntax",
    "What is the meta tag for responsive design?": "check_html_syntax",
    "How do you pause execution in DevTools?": "check_js_logic",
    "How do you declare a block-scoped variable that cannot be reassigned?": "check_js_logic",
    "How do you add a new element to the end of an array in JavaScript?": "check_js_logic",
    "How do you list all databases in MySQL?": "check_sql_security",
    "How do you ensure a column disallows NULL values in MySQL?": "check_sql_security",
    "What command undoes transaction changes in MySQL?": "check_sql_security"
}

# 4. MULTI-TURN CONVERSATIONAL HISTORY (5-Message Array for Phase 3)
MULTI_TURN_HISTORY = [
    HumanMessage(content="How do I filter rows in MySQL?"),
    AIMessage(content="", tool_calls=[{"name": "check_sql_security", "args": {"query": "filter rows"}, "id": "call_abc123"}]),
    ToolMessage(content="SELECT * FROM table_name WHERE condition; -- Filter rows", name="check_sql_security", tool_call_id="call_abc123"), #[cite: 2]
    AIMessage(content="You can filter rows using the WHERE clause. For example: SELECT * FROM table_name WHERE condition;"), #[cite: 2]
    HumanMessage(content="Great, thank you! That perfectly answers my database question.")
]

# 5. SAMPLE CONTEXTS (Simulating tools/rag_retriever.py outputs)
SAMPLE_CONTEXTS = [
    "There are six levels of headings. <h1> is the most important (largest), and <h6> is the least important (smallest).", #[cite: 1]
    "Use defer to ensure scripts run after HTML is parsed.", #[cite: 3]
    "A database is a structured collection of interrelated data stored together to serve multiple applications." #[cite: 2]
]