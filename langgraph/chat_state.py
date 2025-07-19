from typing import TypedDict, List, Tuple
class ChatState(TypedDict, total=False):
    question: str
    chat_history: List[Tuple[str, str]]
    context_docs: List[str]
    answer: str
    next_step: str