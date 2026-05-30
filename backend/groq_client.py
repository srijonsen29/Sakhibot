import time
from groq import Groq, RateLimitError, APIStatusError
from config import GROQ_API_KEY, LLM_MODELS

_client = Groq(api_key=GROQ_API_KEY)


def chat(
    messages: list,
    temperature: float = 0.1,
    max_tokens: int = 1024
) -> str:
    """
    Send messages to Groq with automatic model fallback.

    Tries each model in LLM_MODELS in order.
    If rate limited, waits briefly and tries next model.
    Returns the response text.
    """
    last_error = None

    for i, model in enumerate(LLM_MODELS):
        try:
            print(f"  [GROQ] Trying model: {model}")
            response = _client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            text = response.choices[0].message.content.strip()
            print(f"  [GROQ] Success with: {model}")
            return text

        except RateLimitError as e:
            print(f"  [GROQ] Rate limit on {model} — trying next model...")
            last_error = e
            # small delay before trying next model
            time.sleep(1)
            continue

        except APIStatusError as e:
            if "decommissioned" in str(e).lower() or "not supported" in str(e).lower():
                print(f"  [GROQ] Model {model} decommissioned — skipping...")
                last_error = e
                continue
            else:
                print(f"  [GROQ] API error on {model}: {e}")
                last_error = e
                continue

        except Exception as e:
            print(f"  [GROQ] Unexpected error on {model}: {e}")
            last_error = e
            continue

    # all models failed
    print(f"  [GROQ] All models exhausted. Last error: {last_error}")
    return (
        "I am currently unable to process your request due to high demand. "
        "Please try again in a few minutes, or call 181 (Women's Helpline) "
        "for immediate assistance."
    )