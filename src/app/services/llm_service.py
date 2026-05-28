from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

import json


# ============================================================
# 🔹 LLM INITIALIZATION
# ============================================================

llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0.0
)


# ============================================================
# 🔹 INTENT CLASSIFICATION
# ============================================================

async def classify_intent_llm(user_input: str):

    prompt = ChatPromptTemplate.from_template("""
You are an intent classification engine.

Your task is to classify the user query into ONE of these intents.

AVAILABLE INTENTS:

------------------------------------------------
1. EXPLANATION
------------------------------------------------

General financial knowledge, concepts, or education.

Examples:
- What is EMI?
- Explain compound interest
- What is a credit score?
- What is repo rate?
- Explain inflation

------------------------------------------------
2. CALCULATE_EMI
------------------------------------------------

EMI or loan calculations involving numbers.

Examples:
- Calculate EMI for 5 lakh loan
- EMI for 20 years at 8%
- Monthly payment for 10L loan
- Home loan EMI for 30 lakh

------------------------------------------------
3. POLICY_QUERY
------------------------------------------------

Questions related to:
- Bank policies
- Home loan products
- Interest rates
- Repo linkage
- Processing fees
- Penal charges
- Eligibility
- LTV ratio
- Mortgage rules
- Financial document queries

Examples:
- SBI LTV ratio
- HDFC floating rate linked to?
- Compare SBI vs HDFC rates
- Who is eligible for Shaurya loan?
- SBI processing fee
- HDFC interest rate structure

------------------------------------------------

CLASSIFICATION RULES:

- If query references SBI/HDFC/ICICI/etc → likely POLICY_QUERY
- If query asks about rates/rules/eligibility/policies → POLICY_QUERY
- If query asks for EMI calculation → CALCULATE_EMI
- Otherwise → EXPLANATION

IMPORTANT:
Return ONLY valid JSON.

FORMAT:

{{
  "intent": "<INTENT_NAME>"
}}

USER QUERY:
{user_input}
""")

    chain = prompt | llm

    print("\n⚡ Running intent classification...")

    response = await chain.ainvoke({
        "user_input": user_input
    })

    raw = response.content.strip()

    print(f"🧠 Intent raw response: {raw}")

    # ========================================================
    # SAFE JSON PARSING
    # ========================================================

    try:

        parsed = json.loads(raw)

        intent = parsed.get(
            "intent",
            "EXPLANATION"
        )

        allowed_intents = [
            "EXPLANATION",
            "CALCULATE_EMI",
            "POLICY_QUERY"
        ]

        if intent not in allowed_intents:

            print(
                f"⚠️ Invalid intent returned: {intent}"
            )

            return "EXPLANATION"

        print(f"✅ Classified Intent: {intent}")

        return intent

    except Exception as e:

        print(
            f"❌ Intent parse failed: {str(e)}"
        )

        return "EXPLANATION"


# ============================================================
# 🔹 RESPONSE GENERATION
# ============================================================

async def generate_response_llm(
    user_input,
    structured_data,
    memory
):

    summary = memory.get(
        "summary",
        ""
    )

    recent = memory.get(
        "recent_messages",
        []
    )

    recent_text = "\n".join(
        [
            f"{m['role']}: {m['content']}"
            for m in recent
        ]
    )

    intent = structured_data.get(
        "intent"
    )

    data = structured_data.get(
        "data"
    )

    prompt = ChatPromptTemplate.from_template("""
You are a financial assistant.

RULES:
- Use ONLY the provided structured data when available
- DO NOT hallucinate
- DO NOT invent financial values
- Keep answers concise and clear
- If information is unavailable, say:
  "I don't have enough information"

------------------------------------------------

CONTEXT SUMMARY:
{summary}

------------------------------------------------

RECENT CONVERSATION:
{recent_text}

------------------------------------------------

USER QUERY:
{user_input}

------------------------------------------------

INTENT:
{intent}

------------------------------------------------

STRUCTURED DATA:
{data}

------------------------------------------------

INSTRUCTIONS:

1. If intent = EXPLANATION:
- Answer using general financial knowledge
- Keep explanation simple and concise

2. If intent = CALCULATE_EMI:
- Use ONLY provided calculation data
- Return concise EMI explanation
- Return the answer in a proper format, for example: 
📊 EMI Calculation Result

Monthly EMI: ₹10,501.65
Total Payment: ₹63,009.90
Total Interest Paid: ₹3,009.90

Interest Rate: 17%
Tenure: 6 months       
                                                     
- DO NOT return the answer in formats like these:     
"INTENT: CALCULATE_EMI\n\nEMI (Equated Monthly Installment) for the iPhone loan:\n\nMonthly EMI amount: Rs. 10501.65\nTotal amount at the end of 6 months: Rs. 63009.9"                                                                                           

- DO NOT INCLUDE the INTENT in the final answer
                                                                                      
3. If intent = POLICY_QUERY:
- Use ONLY RAG/generated policy response
- DO NOT add external knowledge

4. If data is missing:
- Say:
  "I don't have enough information"

------------------------------------------------

FINAL ANSWER:
""")

    chain = prompt | llm

    print("\n🤖 Generating final response...")

    response = await chain.ainvoke({

        "summary": summary,

        "recent_text": recent_text,

        "user_input": user_input,

        "intent": intent,

        "data": data
    })

    final_answer = response.content.strip()

    print(
        f"✅ Final response generated: "
        f"{final_answer[:150]}"
    )

    return final_answer


# ============================================================
# 🔹 SUMMARY GENERATION
# ============================================================

async def generate_summary_llm(
    old_summary,
    recent_text
):

    prompt = ChatPromptTemplate.from_template("""
You are summarizing a financial conversation.

PREVIOUS SUMMARY:
{old_summary}

------------------------------------------------

NEW MESSAGES:
{recent_text}

------------------------------------------------

INSTRUCTIONS:
- Keep summary concise
- Preserve important financial context
- Remove redundancy
- Maintain continuity for future conversations

------------------------------------------------

UPDATED SUMMARY:
""")

    chain = prompt | llm

    print("\n📝 Updating conversation summary...")

    response = await chain.ainvoke({

        "old_summary": old_summary,

        "recent_text": recent_text
    })

    summary = response.content.strip()

    print("✅ Summary updated")

    return summary