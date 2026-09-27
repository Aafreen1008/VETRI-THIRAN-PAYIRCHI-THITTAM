import json, re
from typing import Any
from .config import GEMINI_API_KEY, GEMINI_MODEL

try:
    from google import genai
    from google.genai import types
except Exception:
    genai = None
    types = None


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
        text = re.sub(r"\s*```$", "", text)
    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        raise ValueError("AI response did not contain JSON")
    return json.loads(match.group(0))


def _client():
    if not GEMINI_API_KEY or genai is None:
        return None
    return genai.Client(api_key=GEMINI_API_KEY)


def generate_planner(kind: str, payload: dict[str, Any], fallback_fn) -> dict[str, Any]:
    client = _client()
    if client is None:
        result = fallback_fn(payload)
        result["ai_mode"] = "fallback"
        return result

    prompts = {
        "home": "Create a practical Indian home budget recommendation.",
        "party": "Create a practical Indian event/party budget recommendation.",
        "jewelry": "Create a practical fashion-jewellery budget recommendation.",
    }
    schema = {
        "type":"object",
        "properties":{
            "summary":{"type":"string"},
            "budget":{"type":"number"},
            "budget_breakdown":{"type":"array","items":{"type":"object","properties":{
                "name":{"type":"string"},"category":{"type":"string"},"quantity":{"type":"number"},"estimated_cost":{"type":"number"},"search_terms":{"type":"string"},"shopping_links":{"type":"object"}
            },"required":["name","category","estimated_cost","search_terms"]}},
            "remaining_budget":{"type":"number"},
            "tips":{"type":"array","items":{"type":"string"}}
        },
        "required":["summary","budget","budget_breakdown","remaining_budget","tips"]
    }
    instruction = f"""{prompts.get(kind)} You are a budgeting assistant, not a financial adviser. Use INR only. Stay at or below the supplied total budget. Do not recommend restricted goods or services. Return ONLY JSON matching the schema. Make estimates realistic but clearly estimates. Payload: {json.dumps(payload, ensure_ascii=False)}"""
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=instruction,
            config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=schema, temperature=0.3, max_output_tokens=1800),
        )
        result = _extract_json(response.text)
        result["ai_mode"] = "gemini"
        # Safety/correctness guard: never let AI exceed the user's budget.
        budget = float(payload["total_budget"])
        total = sum(float(x.get("estimated_cost",0)) for x in result.get("budget_breakdown",[]))
        if total > budget and total > 0:
            factor=budget/total
            for x in result["budget_breakdown"]:
                x["estimated_cost"]=round(float(x.get("estimated_cost",0))*factor,2)
            result["remaining_budget"]=0
        for x in result.get("budget_breakdown",[]):
            term=x.get("search_terms","")
            if term:
                from .recommendations import links
                x["shopping_links"]=links(term)
        return result
    except Exception:
        result=fallback_fn(payload)
        result["ai_mode"]="fallback"
        result["ai_note"]="Gemini was unavailable, so PocketSmart used its local recommendation engine."
        return result


def chat(message: str) -> str:
    client=_client()
    if client is None:
        return "I can help you split a budget into needs, optional items, and a small buffer. Tell me your total budget and what you are planning."
    try:
        response=client.models.generate_content(
            model=GEMINI_MODEL,
            contents=message,
            config=types.GenerateContentConfig(system_instruction="You are PocketSmart, a concise budgeting assistant. Give general educational budgeting guidance, use INR examples when useful, and avoid presenting estimates as guaranteed prices or personalized financial advice.", temperature=0.4, max_output_tokens=700)
        )
        return response.text.strip()
    except Exception:
        return "The AI service is temporarily unavailable. You can still use the Home, Party and Jewelry planners with PocketSmart's built-in budget engine."
