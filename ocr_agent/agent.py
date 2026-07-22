from google.adk.agents.llm_agent import Agent

root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash",
    description="Document OCR agent",

    instruction="""
You are a document OCR agent.

If the user uploads an image:
- Extract all visible text
- Preserve tables if possible
- Return the entire content
"""
)