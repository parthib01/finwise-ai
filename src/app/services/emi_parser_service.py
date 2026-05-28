from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
import json
import re

# ============================================================
# 🔹 LLM
# ============================================================

llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0
)


# ============================================================
# 🔹 EMI PARAMETER EXTRACTION
# ============================================================

async def extract_emi_parameters(
    user_input: str
):

    prompt = ChatPromptTemplate.from_template("""
You are a financial query parser.

Extract EMI calculation parameters from the user query.

Extract:
- principal
- interest_rate
- tenure_months

RULES:
- tenure must ALWAYS be converted into months
- principal should be numeric only
- remove currency symbols
- convert lakhs/lacs into full numbers

- interest_rate should remain as percentage number ONLY
  Examples:
  17% → 17
  8.5% → 8.5

- DO NOT convert percentages into decimals
- remove currency symbols
- convert lakhs/lacs into numbers

If missing, return null.

Return ONLY valid JSON.

FORMAT:

{{
  "principal": number | null,
  "interest_rate": number | null,
  "tenure_months": number | null
}}

USER QUERY:
{user_input}
""")

    chain = prompt | llm

    print("\n⚡ Extracting EMI parameters...")

    response = await chain.ainvoke({

        "user_input": user_input
    })

    raw = response.content.strip()

    print(
        f"🧠 EMI Extraction Raw: {raw}"
    )

    try:

        # ============================================
        # EXTRACT JSON OBJECT FROM RESPONSE
        # ============================================

        json_match = re.search(
            r'\{[\s\S]*?\}',
            raw
        )

        if not json_match:

            raise ValueError(
                "No JSON found in response"
            )

        json_text = json_match.group()

        parsed = json.loads(json_text)

        result = {

            "principal":
                parsed.get(
                    "principal"
                ),

            "interest_rate":
                parsed.get(
                    "interest_rate"
                ),

            "tenure_months":
                parsed.get(
                    "tenure_months"
                )
        }

        print(
            f"✅ Parsed EMI Params: {result}"
        )

        return result

    except Exception as e:

        print(
            f"❌ EMI extraction failed: "
            f"{str(e)}"
        )

        return {

            "principal": None,

            "interest_rate": None,

            "tenure_months": None
        }