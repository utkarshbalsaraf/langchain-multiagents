from langchain.tools import tool

@tool()
def email_agent(message: str) -> str:
    """
    A simple email agent that simulates sending an email.
    """
    # Simulate sending an email (in a real implementation, you would integrate with an email service)
    return f"Email sent with message: {message}"