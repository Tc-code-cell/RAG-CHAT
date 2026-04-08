from typing import List, TypedDict
from langchain_core.messages import BaseMessage


class GraphState(TypedDict, total=False):

    messages: List[BaseMessage]
    context: str
