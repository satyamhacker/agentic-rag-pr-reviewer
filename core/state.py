from typing import TypedDict, Sequence, Annotated
import operator
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    # operator.add ensures messages APPEND (not overwrite) across nodes — Module 3 Level 3.2
    messages: Annotated[Sequence[BaseMessage], operator.add]
    # Supervisor sets this to route traffic to the correct worker node
    next_agent: str
