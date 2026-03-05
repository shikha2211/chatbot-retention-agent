from google.adk.agents import LlmAgent

def create_retention_agent(tools, instruction, description, model):
    """
    Factory function to create a retention LlmAgent with consistent configuration.
    """
    return LlmAgent(
        name="retention_agent",
        model=model,
        description=description,
        instruction=instruction,
        tools=tools,
    )