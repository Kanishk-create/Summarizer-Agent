# summarizer_agent/agent.py
# -----------------------------------------------------------
# Text Summarization Agent built with Google ADK + Gemini
# Accepts a body of text and returns a concise summary.
# -----------------------------------------------------------

from google.adk.agents import Agent


def summarize_text(text: str, max_sentences: int = 3) -> dict:
    """
    Summarize the provided text into a concise number of sentences.

    Args:
        text: The input text to summarize.
        max_sentences: Maximum number of sentences in the summary (default 3).

    Returns:
        A dict with the summary and metadata about the input.
    """
    word_count = len(text.split())
    char_count = len(text)
    return {
        "status": "ready_to_summarize",
        "original_word_count": word_count,
        "original_char_count": char_count,
        "max_sentences_requested": max_sentences,
        "text": text,
    }


def classify_sentiment(text: str) -> dict:
    """
    Classify the overall sentiment of the provided text.

    Args:
        text: The input text to classify.

    Returns:
        A dict indicating the sentiment and a brief explanation.
    """
    return {
        "status": "ready_to_classify",
        "text": text,
    }


root_agent = Agent(
    model="gemini-2.0-flash",
    name="summarizer_agent",
    description=(
        "An AI agent that summarizes text and optionally classifies its sentiment. "
        "Given any block of text it produces a concise, human-readable summary "
        "and can also identify whether the tone is positive, negative, or neutral."
    ),
    instruction=(
        "You are an expert text summarization and analysis assistant. "
        "When a user provides text:\n"
        "1. Always call the `summarize_text` tool first to analyze the input.\n"
        "2. Return a clear, fluent summary in the requested number of sentences "
        "   (default 3 if not specified). Preserve key facts and main ideas.\n"
        "3. If the user also asks for sentiment, call `classify_sentiment` and "
        "   report whether the text is POSITIVE, NEGATIVE, or NEUTRAL with a "
        "   one-sentence explanation.\n"
        "4. Format your final response as:\n"
        "   **Summary:** <your summary here>\n"
        "   **Sentiment:** <only if requested>\n"
        "   **Stats:** Original text — X words, Y characters.\n"
        "Be concise, accurate, and professional."
    ),
    tools=[summarize_text, classify_sentiment],
)
