from typing import TypedDict, List, Annotated
import operator

class AgentState(TypedDict):
    messages: Annotated[List[str], operator.add]
    # Add other state variables here
