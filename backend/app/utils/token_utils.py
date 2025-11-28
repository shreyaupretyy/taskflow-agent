"""
Utility functions for token counting and text processing
"""


def estimate_tokens(text: str) -> int:
    """
    Estimate token count for text.
    Rough approximation: ~4 characters per token for English text.
    """
    if not text:
        return 0
    
    # Simple estimation: words * 1.3 (accounts for punctuation and special tokens)
    words = len(text.split())
    return int(words * 1.3)


def count_tokens_in_conversation(messages: list) -> int:
    """
    Count tokens in a list of messages.
    """
    total = 0
    for msg in messages:
        if isinstance(msg, dict) and "content" in msg:
            total += estimate_tokens(msg["content"])
        elif isinstance(msg, str):
            total += estimate_tokens(msg)
    return total


def truncate_text(text: str, max_length: int = 1000) -> str:
    """
    Truncate text to maximum length while preserving word boundaries.
    """
    if len(text) <= max_length:
        return text
    
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    
    if last_space > 0:
        return truncated[:last_space] + "..."
    return truncated + "..."
