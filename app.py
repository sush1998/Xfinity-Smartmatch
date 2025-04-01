import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib
import json



st.set_page_config(page_title="Xfinity SmartMatch", layout="wide")


st.markdown("""
    <style>
    body {
        font-family: 'Inter', 'Segoe UI', sans-serif;
        background-color: #280e8b;
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
        color: #1e293b;
        font-weight: 600;
        text-align: center;
    }
    h4 {
        color: #64748b;
        font-weight: 400;
        text-align: center;
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
    }
    .toggle-card:hover {
        transform: translateY(-3px);
    }
    .plan-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #3b82f6;
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
        padding: 15px;
        border-radius: 10px;
        margin: 20px 0;
    }
    .user-message {
        background-color: #e2e8f0;
        color: #1e293b;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 10px;
        word-wrap: break-word;
    }
    .bot-message {
        background-color: #6b7280;
        color: white;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)


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


def get_LLM_response(prompt, keywords=""):
    
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

    
    try:
        with open('Xfinity_data.json', 'r') as file:
            xfinity_products = json.load(file)
    except FileNotFoundError:
        st.error("Xfinity_data.json file not found")
        return [{"name": "Error", "price": "N/A", "features": ["Data file missing"]}]

    context = f"""
        You are a helpful assistant. Respond ONLY with a valid JSON list. DO NOT include explanations or text outside the JSON.

        We have the following Xfinity products under 4 categories: {json.dumps(xfinity_products)}. 
        Users can be recommended a single service or a combination of them based on their input.
        Recognize use cases that require dynamic internet speeds and differentiate between Mobile, TV, Home Security, and Internet use cases.

        Use case: {prompt}
        Keywords: {keywords}

        Return a JSON list of one or more services that best fit the user's needs.
        Each item must follow this format:
        {{
            "name": "Product Name",
            "price": "$XX.XX/month",
            "features": ["feature1", "feature2"]
        }}
    """

    try:
        
        model = genai.GenerativeModel("gemini-2.0-flash")  
        
        response = model.generate_content(
            context,
            generation_config={
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
                "response_mime_type": "application/json"
            }
        )

        # JSON parsing
        if response.text:
            parsed_response = json.loads(response.text)
            if (isinstance(parsed_response, list) and 
                all(isinstance(item, dict) and "name" in item and "price" in item and "features" in item 
                    for item in parsed_response)):
                return parsed_response[:3]  # Return only 3 recommendations
            else:
                st.error(f"Invalid response format: {parsed_response}")
                return [{"name": "Error", "price": "N/A", "features": ["Invalid response format"]}]
        else:
            return [{"name": "Error", "price": "N/A", "features": ["No response generated"]}]

    except json.JSONDecodeError as e:
        st.error(f"JSON parsing error: {e}")
        return [{"name": "Error", "price": "N/A", "features": ["Failed to parse response"]}]
    except Exception as e:
        st.error(f"LLM error: {e}")
        return [{"name": "Error", "price": "N/A", "features": [str(e)]}]


# Streamlit App loading here
def app():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'logged_in' in st.session_state:
        st.session_state.chat_mode=True
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
            st.markdown(f"<h2>Welcome, {st.session_state.user_data['name']} 👋</h2>", unsafe_allow_html=True)
            st.markdown("<h4>Find Your Perfect Xfinity Plan</h4>", unsafe_allow_html=True)            
           
            #  cards
            st.subheader("What are you interested in?")
            st.markdown('<div class="toggle-container">', unsafe_allow_html=True)
            options = ["Internet", "TV", "Mobile", "Home Security"]
            cols = st.columns(4)
            for i, option in enumerate(options):
                with cols[i]:
                    if st.button(option, key=option):
                        st.session_state.active_toggle = option
                        st.session_state.chat_mode = True
                        recommendations = get_LLM_response(f"Show me {option} plans", st.session_state.active_toggle)
                        st.session_state.chat_history = [{"user": f"Show me {option} plans", "bot": recommendations}]
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

            # chat history
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
            # Input prompt
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    user_prompt = st.text_input("", placeholder="Describe your needs...", key="user_input", help="Example: 'I work from home and need fast internet.'")
                    if st.button("Get Recommendations", use_container_width=True):
                        if user_prompt:
                            recommendations = get_LLM_response(user_prompt, st.session_state.active_toggle)
                            st.session_state.chat_history.append({"user": user_prompt, "bot": recommendations})
                            st.rerun()
                        else:
                            st.warning("Please enter a prompt.")

        else:
            login_or_signup()

        st.markdown("</div>", unsafe_allow_html=True)

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