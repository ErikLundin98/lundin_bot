from difflib import SequenceMatcher

def is_similar(sentence: str, sentence_to_compare_to: str, threshold: float) -> bool:
    """Simple similarity check between two sentence."""
    return SequenceMatcher(None, sentence, sentence_to_compare_to).ratio() >= threshold


def contains_wake_word(sentence: str, wake_word: str, threshold: float) -> bool:
    """Check if sentence begins with wake word."""
    wake_word_len = len(wake_word.split(" "))
    potential_wake_word = " ".join(sentence.split(" ")[:wake_word_len])
    return is_similar(potential_wake_word, wake_word, threshold)