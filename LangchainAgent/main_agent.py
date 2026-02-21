from dataclasses import dataclass
from typing import Callable
from langchain.tools import tool, ToolRuntime
from langgraph.types import Command
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain.agents import create_agent, AgentState
from langchain.messages import ToolMessage
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse,HumanInTheLoopMiddleware, dynamic_prompt

load_dotenv()

@dataclass
class EmailContext:
    email: str = "uttub142@gmail.com"
    password: str = "password123"


class AuthenticationState(AgentState):
    authenticated: bool
    
@tool
def check_inbox() -> str:
    """Check the inbox for recent emails"""

    return """
    Hi Julie,
    I'm going to be in town next week and was wondering if we could grab a coffee?
    - best, Jane (jane@example.com)
    """

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an response email"""
    return f"Email sent to {to} with subject {subject} and body {body}"

@tool
def authenticate(email:str, password:str, runtime:ToolRuntime) -> Command:
    """Authenticate the user with the provided email and password"""
    if email == runtime.context.email and password == runtime.context.password:
        return Command(update={
            "authenticated": True,
            "message": [ToolMessage(
                "Successfully authenticated!",
                tool_call_id = runtime.tool_call_id
            )]
        })
        
    else:
        return Command(update={
            "authenticated": False,
            "message": [ToolMessage(
                "Authentication failed. Please check your email and password.",
                tool_call_id = runtime.tool_call_id
            )]
        })
        
@wrap_model_call
def dynamic_tool_call(request: ModelRequest, handler:Callable[[ModelRequest],ModelResponse]) -> ModelResponse:
    """A middleware that dynamically adds tools based on the agent's state"""
    
    authenticated = request.state.get("authenticated")
    
    if authenticated:
        tools =[check_inbox, send_email ]
    else:
        tools = [authenticate]
    
    request = request.override(tools=tools)
    return handler(request)
    
authenticated_prompt = "You are a helpful assistant that can check the inbox and send emails."
unauthenticated_prompt = "You are a helpful assistant that can authenticate users."

@dynamic_prompt
def get_dynamic_prompt(request:ModelRequest) -> str:
    authenticated = request.state.get("authenticated")
    
    if authenticated:
        return authenticated_prompt
    else:
        return unauthenticated_prompt
    
model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.2,
    max_output_tokens=2000,
    streaming=True
)

final_agent = create_agent(
    model=model,
    tools=[check_inbox, send_email, authenticate],
    checkpointer=InMemorySaver(),
    state_schema=AuthenticationState,
    context_schema=EmailContext,
    middleware=[
        dynamic_tool_call,
        get_dynamic_prompt,
        HumanInTheLoopMiddleware(
            interrupt_on={
                "authenticate": False,
                "check_inbox": False,
                "send_email": True
            }
        )
        ],
    system_prompt="You are a helpful assistant. who response in one line",
)

# result = final_agent.invoke({"messages": [{"role": "user", "content": "What's the weather in NYC?"}]})
# print("\nResult:")
# pprint.pprint(result)
# print("\n\nFinalAnswer:",result["messages"][-1].content[0]["text"])