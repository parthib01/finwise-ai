from app.services.llm_service import generate_summary_llm

async def generate_summary(old_summary: str, recent_messages: list):
    recent_text = "\n".join(
        [f"{m['role']}: {m['content']}" for m in recent_messages]
    )

    new_summary = await generate_summary_llm(
        old_summary=old_summary,
        recent_text=recent_text
    )

    return new_summary