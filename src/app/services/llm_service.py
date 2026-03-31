from langchain_ollama import ChatOllama 
from langchain_core.prompts import ChatPromptTemplate
import json


# 🔹 Initialize local LLM (Ollama)
llm = ChatOllama(
    model="phi",   # or mistral / llama2
    temperature=0.0
)

# ============================================================
# 🔹 INTENT CLASSIFICATION
# ============================================================

async def classify_intent_llm(user_input: str):

    prompt = ChatPromptTemplate.from_template("""
You are an intent classifier.

Available intents:
1. EXPLANATION → definition, meaning, concept (e.g., "What is EMI?", "Define credit score")
2. CALCULATE_EMI → EMI calculation queries with numbers (e.g., "EMI for 5L loan")
3. CATEGORY_SPEND → spending queries (e.g., "How much did I spend?")

Rules:
- Return ONLY JSON
- Do NOT explain
- Do NOT add extra text

Output format:
{{
  "intent": "<INTENT_NAME>"
}}

User Query:
{user_input}
""")

    chain = prompt | llm

    response = await chain.ainvoke({
        "user_input": user_input
    })

    try:
        parsed = json.loads(response.content)
        return parsed.get("intent", "EXPLANATION")
    except:
        return "EXPLANATION"  # safe fallback


# ============================================================
# 🔹 RESPONSE GENERATION
# ============================================================

async def generate_response_llm(user_input, structured_data, memory):

    summary = memory.get("summary", "")
    recent = memory.get("recent_messages", [])

    recent_text = "\n".join(
        [f"{m['role']}: {m['content']}" for m in recent]
    )

    intent = structured_data.get("intent")
    data = structured_data.get("data")

    prompt = ChatPromptTemplate.from_template("""
You are a STRICT financial assistant.

RULES:
- You MUST use ONLY the provided data.
- DO NOT use external knowledge.
- DO NOT guess or hallucinate.
- Keep answers short and clear.

Context Summary:
{summary}

Recent Conversation:
{recent_text}

User Query:
{user_input}

Intent:
{intent}

Structured Data:
{data}

Instructions:
- If intent is EXPLANATION → answer normally using general knowledge
- If data is present → use it strictly
- If data is missing AND not explanation → say "I don't have enough information"
- Keep answers short and clear
                                              
Answer:
""")

    chain = prompt | llm

    response = await chain.ainvoke({
        "summary": summary,
        "recent_text": recent_text,
        "user_input": user_input,
        "intent": intent,
        "data": data
    })

    return response.content


# ============================================================
# 🔹 SUMMARY GENERATION
# ============================================================

async def generate_summary_llm(old_summary, recent_text):

    prompt = ChatPromptTemplate.from_template("""
You are summarizing a financial conversation.

Previous Summary:
{old_summary}

New Messages:
{recent_text}

Instructions:
- Keep it concise
- Retain important financial context
- Remove redundancy

Updated Summary:
""")

    chain = prompt | llm

    response = await chain.ainvoke({
        "old_summary": old_summary,
        "recent_text": recent_text
    })

    return response.content