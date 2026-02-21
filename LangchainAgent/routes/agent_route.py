from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import json
from pydantic import BaseModel
from main_agent import EmailContext, final_agent

class AgentInput(BaseModel):
    question:str
    conversation_id: int = 123
    
router = APIRouter()

@router.post("/agent")
def agent_endpoint(input: AgentInput):
    try:
        async def event_generator():
            try:
                config = {"configurable":{"thread_id": input.conversation_id}}
                for event in final_agent.stream(
                    {"messages": [{"role": "user", "content": input.question}]},
                    config=config,
                    context=EmailContext(),
                    stream_mode="messages"
                ):
                    # Extract content from the event
                    text = event[0].content
                    print("Event:", text)
                    
                    # Create data payload
                    data = {
                        "delta": text,
                        "error": "",
                        "final_response": ""
                    }
                    
                    # Send as SSE format: "data: {json}\n\n"
                    yield f"data: {json.dumps(data)}\n\n"
                
                # Send final event
                final_data = {
                    "delta": "",
                    "error": "",
                    "final_response": "complete"
                }
                yield f"data: {json.dumps(final_data)}\n\n"
                
            except Exception as e:
                error_data = {
                    "delta": "",
                    "error": str(e),
                    "final_response": ""
                }
                yield f"data: {json.dumps(error_data)}\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    except Exception as e:
        print("Error",str(e))
        return {"error": str(e)}