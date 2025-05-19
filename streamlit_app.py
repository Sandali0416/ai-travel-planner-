import os
import streamlit as st
from dotenv import load_dotenv
from langchain import OpenAI
from langchain.agents import initialize_agent, Tool
from langchain.memory import ConversationBufferMemory
import wikipedia

# Load environment variables from .env
load_dotenv()

# Retrieve OpenAI key
openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    st.error("Missing OPENAI_API_KEY in .env file. Please add it and restart.")
    st.stop()

# Initialize OpenAI LLM
llm = OpenAI(
    openai_api_key=openai_key,
    temperature=0.7
)

# Memory for conversation history
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

# Tool: Wikipedia search + summary
def wiki_search_and_summarize(query: str) -> str:
    """
    Search Wikipedia and return a 3-sentence summary of the top result.
    """
    try:
        results = wikipedia.search(query)
        if not results:
            return "I couldn't find information on that topic. Try rephrasing."
        summary = wikipedia.summary(results[0], sentences=3)
        return summary
    except Exception as e:
        return f"Error retrieving information: {e}"

wiki_tool = Tool(
    name="WikiSearch",
    func=wiki_search_and_summarize,
    description="Useful for looking up travel destination details from Wikipedia."
)

# Initialize agent with tool and memory
agent = initialize_agent(
    tools=[wiki_tool],
    llm=llm,
    agent="conversational-react-description",
    memory=memory,
    verbose=False
)

# Streamlit UI settings
st.set_page_config(page_title="AI Travel Planner", layout="centered")
st.title("✈️ AI Travel Itinerary Planner")
st.write("Plan personalized travel itineraries with AI-powered reasoning and memory.")

# User input area
user_input = st.text_area("Enter your travel preferences or questions:", height=150)

if st.button("Plan My Trip"):
    if user_input.strip():
        with st.spinner("Generating itinerary..."):
            response = agent.run(user_input)
        st.markdown("**Agent:**")
        st.write(response)
    else:
        st.warning("Please enter your preferences or a question to get started.")
