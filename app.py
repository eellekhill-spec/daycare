import streamlit as st
import anthropic
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="Nashville Daycare Price Monitor",
    page_icon="🏫",
    layout="wide"
)

# Initialize Anthropic client
# Replace 'your-api-key-here' with your actual API key
ANTHROPIC_API_KEY = st.secrets ["ANTHROPIC_API_KEY"]
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

st.title("🏫 Nashville Daycare Price Monitor")
st.markdown("Get real-time information about daycare prices in Nashville, TN")

# Sidebar for search options
with st.sidebar:
    st.header("Search Options")
    search_area = st.text_input(
        "Specific Area/Neighborhood",
        placeholder="e.g., East Nashville, Green Hills"
    )
    age_group = st.selectbox(
        "Age Group",
        ["All Ages", "Infants (0-12 months)", "Toddlers (1-3 years)", 
         "Preschool (3-5 years)", "School Age (5+ years)"]
    )
    price_range = st.selectbox(
        "Price Range",
        ["Any", "Under $200/week", "$200-$300/week", 
         "$300-$400/week", "Over $400/week"]
    )

# Main search interface
query = st.text_area(
    "What would you like to know about Nashville daycare prices?",
    placeholder="Example: What are the average daycare prices in East Nashville for toddlers?",
    height=100
)

if st.button("Search", type="primary"):
    if not query:
        st.warning("Please enter a question about daycare prices.")
    else:
        with st.spinner("Searching for daycare information..."):
            # Build the search prompt
            search_context = f"Location: Nashville, TN"
            if search_area:
                search_context += f", specifically {search_area}"
            if age_group != "All Ages":
                search_context += f"\nAge Group: {age_group}"
            if price_range != "Any":
                search_context += f"\nPrice Range: {price_range}"
            
            full_query = f"{search_context}\n\nUser Question: {query}"
            
            try:
                # Make API call with web search tool
                message = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=4096,
                    tools=[
                        {
                            "type": "web_search_20250305",
                            "name": "web_search"
                        }
                    ],
                    messages=[
                        {
                            "role": "user",
                            "content": full_query
                        }
                    ]
                )
                
                # Process the response
                response_text = ""
                tool_uses = []
                
                for block in message.content:
                    if block.type == "text":
                        response_text += block.text
                    elif block.type == "tool_use":
                        tool_uses.append(block)
                
                # Display results
                st.success("Search Complete!")
                
                # Show the main response
                st.markdown("### Results")
                st.markdown(response_text)
                
                # Show search queries used (optional debug info)
                if tool_uses and st.checkbox("Show search details"):
                    st.markdown("### Search Queries Used")
                    for tool in tool_uses:
                        if hasattr(tool, 'input'):
                            st.info(f"🔍 Searched: {tool.input.get('query', 'N/A')}")
                
                # Display timestamp
                st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.info("Please check your API key and try again.")

# Information section
with st.expander("ℹ️ About This Tool"):
    st.markdown("""
    This app uses Claude AI with web search capabilities to find current information about 
    daycare prices in Nashville, TN.
    
    **How to use:**
    1. Enter your question about daycare prices
    2. Optionally filter by area, age group, or price range
    3. Click "Search" to get real-time information
    
    **Example questions:**
    - What are the average daycare prices in Nashville?
    - Compare daycare costs in Green Hills vs East Nashville
    - What's the typical cost for infant care in Nashville?
    - Are there affordable daycare options near downtown Nashville?
    
    **Note:** Prices and availability change frequently. Always contact facilities directly 
    to confirm current rates and openings.
    """)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray;'>Powered by Claude AI with Web Search</p>",
    unsafe_allow_html=True
)
