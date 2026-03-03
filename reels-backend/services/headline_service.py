# reels-backend/services/headline_service.py  — full replacement

import json
import re

OLLAMA_MODEL = "mistral"   # using your installed model


def generate_headlines_from_transcript(transcript: str) -> list:
    """Try Ollama first, smart fallback if fails"""
    print(f"✍️ Generating headlines... transcript length: {len(transcript)}")

    if not transcript or len(transcript.strip()) < 10:
        print("⚠️ Transcript too short — using fallback")
        return get_default_headlines()

    try:
        import ollama

        short_transcript = transcript[:500].strip()

        prompt = f"""Generate exactly 3 short punchy video headlines.
Rules:
- 5 to 8 words each
- Attention grabbing
- No hashtags, no emojis
- Return ONLY a JSON array like: ["Headline 1", "Headline 2", "Headline 3"]

Transcript: "{short_transcript}"

JSON array:"""

        print(f"📡 Calling Ollama ({OLLAMA_MODEL})...")

        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.8, "num_predict": 200}
        )

        response_text = response["message"]["content"].strip()
        print(f"🤖 Ollama response: {response_text[:200]}")

        headlines = parse_headlines_from_response(response_text)
        print(f"✅ Headlines generated: {headlines}")
        return headlines

    except ImportError:
        print("❌ ollama package not installed — run: pip install ollama")
        return get_default_headlines()
    except Exception as e:
        print(f"❌ Ollama error: {e}")
        return get_default_headlines()


def parse_headlines_from_response(response_text: str) -> list:
    # Try direct JSON parse
    try:
        headlines = json.loads(response_text)
        if isinstance(headlines, list) and len(headlines) > 0:
            return [clean_headline(h) for h in headlines[:3]]
    except Exception:
        pass

    # Find JSON array in response
    try:
        match = re.search(r'\[.*?\]', response_text, re.DOTALL)
        if match:
            headlines = json.loads(match.group())
            if isinstance(headlines, list) and len(headlines) > 0:
                return [clean_headline(h) for h in headlines[:3]]
    except Exception:
        pass

    # Split by newlines as last resort
    lines = [
        line.strip().strip('"\'').strip("-").strip("*").strip()
        for line in response_text.split("\n")
        if line.strip() and len(line.strip()) > 10
    ]
    if lines:
        return [clean_headline(l) for l in lines[:3]]

    return get_default_headlines()


def clean_headline(text: str) -> str:
    text = str(text).strip()
    text = re.sub(r'^[\d\.\-\*\"\']+\s*', '', text)
    text = text.strip('"\'')
    return text[:80]


def get_default_headlines() -> list:
    return [
        "Watch This Before Everyone Else",
        "This Changes Everything You Know",
        "The Truth Nobody Is Talking About"
    ]