def classify_intent_llm(user_input: str):
    # Temporary stub
    if "spending" in user_input.lower():
        return {
            "intent": "CATEGORY_SPEND",
            "requires_db": True,
            "parameters": {}
        }

    return {
        "intent": "EXPLANATION",
        "requires_db": False,
        "parameters": {}
    }


async def generate_response_llm(user_input, intent, db_result, memory):

    summary = memory.get("summary", "")
    recent = memory.get("recent_messages", [])

    # Convert recent messages to text
    recent_text = "\n".join(
        [f"{m['role']}: {m['content']}" for m in recent]
    )

    # 🔥 This is your prompt (simplified)
    prompt = f"""
    Summary:
    {summary}

    Recent Conversation:
    {recent_text}

    User:
    {user_input}
    """

    # Stub logic (replace later with real LLM)
    if intent == "EXPLANATION":
        return "Explanation with context."

    if intent == "CATEGORY_SPEND":
        return f"You spent ₹{db_result.get('total_spent', 0)}."

    if intent == "CALCULATE_EMI":
        return f"Your EMI is ₹{db_result}"

    return "I couldn't understand."