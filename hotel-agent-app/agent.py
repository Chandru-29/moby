from google.adk.agents import Agent

root_agent = Agent(
    model='gemini-2.5-flash',
    name='hotel_agent',
    description='A helpful assistant that answers questions about a specific city.',
    instruction='Answer user questions about a specific city to the best of your knowledge. Do not answer questions outside of this.',
)