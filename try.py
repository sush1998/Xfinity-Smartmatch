import streamlit as st
import sqlite3
import hashlib
import uuid

# Set page config as the first Streamlit command
st.set_page_config(page_title="Xfinity SmartMatch", layout="wide")

# Custom CSS (unchanged)
st.markdown("""
    <style>
    body {
        font-family: 'Inter', 'Segoe UI', sans-serif;
        background-color: #f0f2f6;
    }
    .main {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 12px;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.05);
        max-width: 900px;
        margin: 0 auto;
    }
    h2 {
        position:relative;
        color: #1e293b;
        font-weight: 600;
    }
    h4 {
        color: #64748b;
        font-weight: 400;
    }
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        padding: 12px;
        background-color: #f9fafb;
        color: #64748b;
    }
    .stTextInput > div > div > input::placeholder {
        color: #64748b;
        opacity: 1;
    }
    .stButton > button {
        background-color: #3b82f6;
        color: white;
        border-radius: 10px;
        padding: 12px 24px;
        border: none;
        font-weight: 500;
        transition: background-color 0.3s ease, transform 0.2s ease;
    }
    .stButton > button:hover {
        background-color: #2563eb;
        transform: translateY(-2px);
    }
    .toggle-container {
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
        justify-content: space-between;
    }
    .toggle-card {
        flex: 1 1 calc(25% - 15px);
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    .toggle-card.active {
        background-color: #3b82f6;
        color: white;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    .toggle-card:hover {
        transform: translateY(-3px);
    }
    .plan-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #3b82f6;
        transition: transform 0.2s ease;
    }
    .plan-card:hover {
        transform: translateY(-5px);
    }
    .plan-card h3 {
        color: #1e293b;
        margin: 0;
        font-size: 1.25rem;
    }
    .plan-card p {
        color: #64748b;
        margin: 5px 0;
    }
    .logout-btn {
        position: fixed;
        top: 20px;
        right: 20px;
    }
    .chat-container {
        background-color: #f3f4f6;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        grid-column-gap: 0px;
        grid-row-gap: 10px;
        }
        .user-message {
            background-color: #e2e8f0;
            color: white;
            padding: 10px;
            border-radius: 10px;
            grid-area: 1 / 3 / 2 / 6;
            justify-items: end;
        }
        .bot-message {
            background-color: #6b7280;
            color: black;
            padding: 10px;
            border-radius: 10px;
            grid-area: 2 / 1 / 3 / 4;
        }
        .chat-space{
            height:2em;
        }
    </style>
""", unsafe_allow_html=True)

# Database functions (unchanged)
def init_db():
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            plans TEXT
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user(username):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def signup_user(username, password, name, age):
    if get_user(username):
        return "Username already exists!"
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    hashed_password = hash_password(password)
    cursor.execute("INSERT INTO users (username, password, name, age, plans) VALUES (?, ?, ?, ?, ?)",
                   (username, hashed_password, name, age, ''))
    conn.commit()
    conn.close()
    return "User signed up successfully! Please log in."

def login_user(username, password):
    user = get_user(username)
    if user and user[2] == hash_password(password):
        return user
    return None

# Improved AI Recommendation Logic
def get_ai_recommendation(prompt, active_toggle):
    if not prompt or not active_toggle:
        return [{"name": "No Plan Available", "price": "N/A", "features": ["Please provide details and select a category"]}]

    prompt = prompt.lower()  # Ensure consistent case for keyword matching

    if active_toggle == "Internet":
        if "work from home" in prompt or "video calls" in prompt or "fast" in prompt:
            return [
                {"name": "Ultimate Connect", "price": "$79.99/mo", "features": ["1 Gbps Internet", "Unlimited Data"]},
                {"name": "Fast Connect", "price": "$59.99/mo", "features": ["500 Mbps Internet", "Unlimited Data"]}
            ]
        elif "gaming" in prompt:
            return [
                {"name": "Gamer Speed", "price": "$69.99/mo", "features": ["800 Mbps Internet", "Low Latency"]},
                {"name": "Ultimate Connect", "price": "$79.99/mo", "features": ["1 Gbps Internet", "Unlimited Data"]}
            ]
        else:
            return [
                {"name": "Basic Speed", "price": "$29.99/mo", "features": ["100 Mbps Internet", "1 TB Data"]}
            ]

    elif active_toggle == "TV":
        if "streaming" in prompt or "netflix" in prompt:
            return [
                {"name": "Streaming Plus", "price": "$99.99/mo", "features": ["500 Mbps Internet", "200+ Channels"]},
                {"name": "Stream Lite", "price": "$69.99/mo", "features": ["300 Mbps Internet", "150+ Channels"]}
            ]
        else:
            return [
                {"name": "Basic TV", "price": "$49.99/mo", "features": ["125+ Channels", "DVR Included"]}
            ]

    elif active_toggle == "Mobile":
        if "unlimited" in prompt or "5g" in prompt:
            return [
                {"name": "Mobile Freedom", "price": "$45.00/mo", "features": ["Unlimited Talk & Text", "5G Network"]}
            ]
        else:
            return [
                {"name": "Mobile Lite", "price": "$25.00/mo", "features": ["10GB Data", "4G Network"]}
            ]

    elif active_toggle == "Home Security":
        if "cameras" in prompt or "smart home" in prompt:
            return [
                {"name": "Total Protection", "price": "$59.99/mo", "features": ["Cameras", "Motion Sensors"]}
            ]
        else:
            return [
                {"name": "Secure Home", "price": "$39.99/mo", "features": ["24/7 Monitoring", "Smart Locks"]}
            ]

    return [{"name": "Generic Plan", "price": "$49.99/mo", "features": ["Basic Features"]}]

def get_LLM_response(prompt, keywords, api_key = "SUPER_SECRET_API_KEY"):

    import base64
    import os
    from google import genai
    from google.genai import types
    import json
    import streamlit as st 

    
    api_key = st.secrets[api_key] 

    with open('Xfinity_data.json', 'r') as file:
        xfinity_products = json.load(file)

    context = f"""
                    We have the following x-finity products under 4 categories as the following: {xfinity_products}. Users can be recommended a single 
                    service or a combination of them based on their input prompt. Based on the user prompt and some keywords, return a list of a total 
                    of three services or three combinations of services (in the same input format) you would deem to be the best fit for their needs. 
                    User prompt: {prompt} Keywords: {keywords}
        """


    def generate():
        client = genai.Client(
            api_key=os.environ.get("GEMINI_API_KEY"),
        )

        model = "gemini-2.0-flash"
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text = context
                    ),
                ],
            ),
        ]
        generate_content_config = types.GenerateContentConfig(
            temperature=1,
            top_p=0.95,
            top_k=40,
            max_output_tokens=8192,
            response_mime_type="application/json",
        )

        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            print(chunk.text, end="")


    llm_response = generate()
    return llm_response


# Streamlit App
def app():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {}
    if 'show_signup' not in st.session_state:
        st.session_state.show_signup = False
    if 'active_toggle' not in st.session_state:
        st.session_state.active_toggle = None
    if 'chat_mode' not in st.session_state:
        st.session_state.chat_mode = False
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    with st.container():
        st.markdown("<div>", unsafe_allow_html=True)
        
        if st.session_state.logged_in:
            # Logout button
            st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.session_state.user_data = {}
                st.session_state.chat_mode = False
                st.session_state.chat_history = []
                st.session_state.active_toggle = None
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown(f"<h2 style='text-align: center;'>Welcome, {st.session_state.user_data['name']} 👋</h2>", unsafe_allow_html=True)
            st.markdown("<h4 style='text-align: center;'>Find Your Perfect Xfinity Plan</h4>", unsafe_allow_html=True)            
            
            # Toggle cards
            st.subheader("What are you interested in?")
            st.markdown('<div class="toggle-container">', unsafe_allow_html=True)
            options = ["Internet", "TV", "Mobile", "Home Security"]
            cols = st.columns(4)
            for i, option in enumerate(options):
                with cols[i]:
                    if st.button(option, key=option):
                        st.session_state.active_toggle = option
                        st.session_state.chat_mode = True
                        recommendations = get_ai_recommendation("", st.session_state.active_toggle)
                        st.session_state.chat_history = [{"user": f"Show me {option} plans", "bot": recommendations}]
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

            if 'chat_mode' in st.session_state:
                st.session_state.chat_mode = True
            if 'chat_history' not in st.session_state:
                st.session_state.chat_history = []
            if 'waiting_for_continue' not in st.session_state:
                st.session_state.waiting_for_continue = False


            # Display chat history
            
            for entry in st.session_state.chat_history:
                for plan in entry['bot']:
                    st.markdown(
                        f"""
                        <div class='chat-container'>
                            <div  class='user-message'>
                                <strong class='user-message'>You:</strong> {entry['user']}
                            </div>
                            <div  class='bot-message'>
                                <strong style='color: #3b82f6;'>SmartMatch: </strong>
                                <div class='plan-card'>
                                    <h3>{plan['name']}</h3>
                                    <p><strong>Price:</strong> {plan['price']}</p>
                                    <p><strong>Features:</strong> {', '.join(plan['features'])}</p>
                                </div>
                            </div>
                        </div>
                        """,
                            unsafe_allow_html=True
                        )

            if st.session_state.chat_mode:
                # Initial prompt input (centered)
                col1, col2, col3 = st.columns([1, 1, 2])
                with col3:
                    st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
                    user_prompt = st.text_input("", placeholder="Describe your needs...", key="initial_user_input", help="Example: 'I work from home and need fast internet.'")
                    print(user_prompt)
                    print(type(user_prompt))
                    st.markdown("</div>", unsafe_allow_html=True)

                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("Get Recommendations", use_container_width=True):
                        if user_prompt:
                            recommendations = get_ai_recommendation(user_prompt, st.session_state.active_toggle)
                            st.session_state.chat_history.append({"user": user_prompt, "bot": recommendations})
                            st.rerun()
                        else:
                            st.warning("Please enter a prompt.")

        else:
            login_or_signup()

        st.markdown("</div>", unsafe_allow_html=True)

# Login & Signup Logic (unchanged)
def login_or_signup():
    if not st.session_state.show_signup:
        st.header("Login to Xfinity SmartMatch")
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")

        if st.button("Login"):
            if not username or not password:
                st.warning("Please fill in all fields.")
            else:
                user = login_user(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_data = {
                        "name": user[3], 
                        "age": user[4], 
                        "plans": user[5].split(',') if user[5] else []
                    }
                    st.rerun()
                else:
                    st.warning("Invalid credentials. Please try again or sign up.")

        if st.button("Need an account? Sign Up"):
            st.session_state.show_signup = True
            st.rerun()
    else:
        signup_form()

def signup_form():
    st.header("Create Your Account")
    new_username = st.text_input("Choose a Username", placeholder="Enter a username")
    new_password = st.text_input("Choose a Password", type="password", placeholder="Enter a password")
    name = st.text_input("Your Name", placeholder="Enter your name")
    age = st.number_input("Your Age", min_value=18, max_value=100, step=1)

    if st.button("Sign Up"):
        if not new_username or not new_password or not name or not age:
            st.warning("Please fill in all fields.")
        else:
            result = signup_user(new_username, new_password, name, age)
            if "successfully" in result:
                st.success(result)
                st.session_state.show_signup = False
                st.rerun()
            else:
                st.error(result)

    if st.button("Back to Login"):
        st.session_state.show_signup = False
        st.rerun()

# Run the app
if __name__ == "__main__":
    init_db()
    app()