import streamlit as st
import pandas as pd
import os

# File to store user data
USER_DATA_FILE = 'users.csv'

# Check if the users file exists, if not create it
if not os.path.exists(USER_DATA_FILE):
    df = pd.DataFrame(columns=['ID', 'Name', 'Last Name', 'Mobile Number', 'Telegram ID', 'Username', 'Password'])
    df.to_csv(USER_DATA_FILE, index=False)

# Load user data from the file
def load_users():
    return pd.read_csv(USER_DATA_FILE)

# Save user data to the file
def save_user(data):
    df = load_users()
    new_user = pd.DataFrame([data])
    df = pd.concat([df, new_user], ignore_index=True)
    df.to_csv(USER_DATA_FILE, index=False)

# Check credentials
def check_credentials(username, password):
    users = load_users()
    user = users[users['Username'] == username]
    if not user.empty:
        stored_password = user.iloc[0]['Password']
        return stored_password == password
    return False

# Sign up page
def sign_up():
    st.title("Sign Up")
    
    with st.form(key='sign_up_form'):
        name = st.text_input("Name", key="name")
        last_name = st.text_input("Last Name", key="last_name")
        mobile_number = st.text_input("Mobile Number", key="mobile_number").replace(",", "")
        telegram_id = st.text_input("Telegram ID", key="telegram_id")
        username = st.text_input("Username", key="username")
        password = st.text_input("Password", type="password", key="password")
        
        submit_button = st.form_submit_button(label='Sign Up')
    
    if submit_button:
        if name and last_name and mobile_number and telegram_id and username and password:
            users = load_users()
            if username in users['Username'].values:
                st.error("Username already exists. Please choose a different username.")
            else:
                user_id = len(users) + 1
                user_data = {
                    'ID': user_id,
                    'Name': name,
                    'Last Name': last_name,
                    'Mobile Number': mobile_number,
                    'Telegram ID': telegram_id,
                    'Username': username,
                    'Password': password
                }
                save_user(user_data)
                st.success("User registered successfully!")
                st.session_state['page'] = 'login'
        else:
            st.error("Please fill out all fields.")
    
    if st.button("Back to Login", key="back_to_login_button"):
        st.session_state['page'] = 'login'

# Login page
def login():
    st.title("Login")
    
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    
    if st.button("Login", key="login_button"):
        if username == "admin" and password == "admin":
            st.session_state['logged_in'] = True
            st.session_state['is_admin'] = True
            st.session_state['page'] = 'admin_panel'
        elif check_credentials(username, password):
            st.session_state['logged_in'] = True
            st.session_state['is_admin'] = False
            st.session_state['page'] = 'user_panel'
        else:
            st.error("Invalid credentials")
    
    if st.button("Go to Sign Up", key="goto_signup_button"):
        st.session_state['page'] = 'sign_up'

# Admin panel
def admin_panel():
    st.title("Admin Panel")
    users = load_users()
    st.write(users)
    if st.button("Logout", key="admin_logout_button"):
        st.session_state['logged_in'] = False
        st.session_state['page'] = 'login'

# User panel
def user_panel():
    st.title("User Panel")
    st.write("Welcome to the user panel!")
    if st.button("Logout", key="user_logout_button"):
        st.session_state['logged_in'] = False
        st.session_state['page'] = 'login'

# Main app logic
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['is_admin'] = False
    st.session_state['page'] = 'login'

if st.session_state['logged_in']:
    if st.session_state['is_admin']:
        admin_panel()
    else:
        user_panel()
else:
    if st.session_state['page'] == 'login':
        login()
    elif st.session_state['page'] == 'sign_up':
        sign_up()
