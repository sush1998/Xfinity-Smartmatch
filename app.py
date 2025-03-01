import streamlit as st
import random

# Sample data for recommendations
sample_recommendations = [
    {
        "id": 1,
        "name": "Ultimate Connect",
        "price": "$79.99/mo",
        "features": ["1 Gbps Internet", "Unlimited Data", "Free WiFi Router", "No Contract"],
        "type": "internet"
    },
    {
        "id": 2,
        "name": "Streaming Plus",
        "price": "$99.99/mo",
        "features": ["500 Mbps Internet", "200+ Channels", "Free DVR", "Premium Streaming"],
        "type": "bundle"
    },
    {
        "id": 3,
        "name": "Mobile Freedom",
        "price": "$45.00/mo",
        "features": ["Unlimited Talk & Text", "15GB High-Speed Data", "5G Network Access", "Family Plan Option"],
        "type": "mobile"
    }
]

# Function to simulate AI recommendation (randomly selecting recommendations for simplicity)
def get_recommendations(user_input):
    # In a real-world scenario, you would use AI to analyze the input and recommend plans
    return random.sample(sample_recommendations, k=3)  # Return 3 random recommendations

# Streamlit app
def app():
    st.set_page_config(page_title="Xfinity SmartMatch", layout="wide")
    
    # Header
    st.markdown("# Xfinity SmartMatch")
    st.markdown("### Find Your Perfect Plan")

    # Login section
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if st.session_state.logged_in:
        st.write("Welcome, User! 🎉")
    else:
        login_button = st.button("Login")
        if login_button:
            st.session_state.logged_in = True

    st.markdown("#### Tell us your needs, and we'll match you with the ideal internet and mobile services.")
    
    # User input section
    user_input = st.text_input("What services are you looking for? (e.g., streaming, work from home, mobile plan)")

    if st.button("Find My Plans"):
        if user_input:
            with st.spinner('Finding your plans...'):
                recommendations = get_recommendations(user_input)
                st.success("Found your recommendations!")
                
                # Display recommendations
                for plan in recommendations:
                    st.subheader(plan['name'])
                    st.markdown(f"**Price**: {plan['price']}")
                    st.markdown("**Features**:")
                    for feature in plan['features']:
                        st.markdown(f"- {feature}")
                    st.markdown("___")
        else:
            st.warning("Please enter your needs to find recommendations.")

    # Footer
    st.markdown("##")
    st.markdown("### Why Use Xfinity SmartMatch?")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.image("https://upload.wikimedia.org/wikipedia/commons/8/80/Serpentine_stone_large.png", width=50)
        st.markdown("**Personalized Matches**")
        st.markdown("Our AI analyzes your unique needs to find the perfect plan for you.")
    
    with col2:
        st.image("https://upload.wikimedia.org/wikipedia/commons/8/80/Serpentine_stone_large.png", width=50)
        st.markdown("**Compare Options**")
        st.markdown("See all available plans side-by-side to make the best decision.")
    
    with col3:
        st.image("https://upload.wikimedia.org/wikipedia/commons/8/80/Serpentine_stone_large.png", width=50)
        st.markdown("**Bundle & Save**")
        st.markdown("Find the best combined packages for internet and mobile services.")
    
    # Footer section
    st.markdown("##")
    st.markdown("© 2025 Xfinity SmartMatch. All rights reserved.")
    st.markdown("[Privacy Policy](#) | [Terms of Service](#) | [Contact Us](#)")

if __name__ == "__main__":
    app()
