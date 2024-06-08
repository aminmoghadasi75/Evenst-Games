import streamlit as st
import pandas as pd
import os
from datetime import datetime

# File paths
USER_DATA_FILE = 'users.csv'
EVENT_DATA_FILE = 'events.csv'
REGISTRATION_DATA_FILE = 'registrations.csv'

# Ensure files exist
for file in [USER_DATA_FILE, EVENT_DATA_FILE, REGISTRATION_DATA_FILE]:
    if not os.path.exists(file):
        if file == USER_DATA_FILE:
            df = pd.DataFrame(columns=['ID', 'Name', 'Last Name', 'Mobile Number', 'Telegram ID', 'Username', 'Password'])
        elif file == EVENT_DATA_FILE:
            df = pd.DataFrame(columns=['EventID', 'Event Name', 'Date', 'Max Volunteers'])
        elif file == REGISTRATION_DATA_FILE:
            df = pd.DataFrame(columns=['UserID', 'EventID'])
        df.to_csv(file, index=False)

# Utility functions

def load_data(file):
    data = pd.read_csv(file, dtype='str')
    for column in data.columns:
        if data[column].dtype == 'object':
            data[column] = data[column].str.strip()
    if 'Max Volunteers' in data.columns:
        data['Max Volunteers'] = data['Max Volunteers'].astype(int)
    return data


def save_data(file, data):
    data.to_csv(file, index=False)


# Check credentials
# Check credentials
def check_credentials(username, password):
    users = load_data(USER_DATA_FILE)
    print("All users loaded from file:")
    print(users)
    user = users[users['Username'] == username]
    print("Filtered user by username:")
    print(user)
    if not user.empty:
        stored_password = user.iloc[0]['Password']
        print("Stored password:", stored_password)
        print("Entered password:", password)
        return stored_password == password
    return False


# Check if username exists
def username_exists(username):
    users = load_data(USER_DATA_FILE)
    return username in users['Username'].values

# Sign up page
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
            if username_exists(username):
                st.error("Username already exists. Please choose a different username.")
            else:
                users = load_data(USER_DATA_FILE)
                user_id = len(users) + 1
                user_data = {
                    'ID': str(user_id),
                    'Name': str(name),
                    'Last Name': str(last_name),
                    'Mobile Number': str(mobile_number),
                    'Telegram ID': str(telegram_id),
                    'Username': str(username),
                    'Password': str(password)
                }
                save_data(USER_DATA_FILE, pd.concat([users, pd.DataFrame([user_data])], ignore_index=True))
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
            st.session_state['username'] = username
            st.session_state['page'] = 'user_panel'
        else:
            st.error("Invalid credentials")
    
    if st.button("Go to Sign Up", key="goto_signup_button"):
        st.session_state['page'] = 'sign_up'

# Admin panel
# Admin panel
# Admin panel
def admin_panel():
    st.title("Admin Panel")
    
    tabs = st.tabs(["Create Event", "View Registered Users", "Remove Event"])
    
    # Create Event tab
    with tabs[0]:
        st.subheader("Create Event")
        with st.form(key='create_event_form'):
            event_name = st.text_input("Event Name", key="event_name")
            event_date = st.date_input("Event Date", key="event_date", min_value=datetime.today())
            event_time = st.time_input("Event Time", key="event_time")
            event_day = st.selectbox("Event Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], key="event_day")
            max_volunteers = st.number_input("Max Volunteers", min_value=1, step=1, key="max_volunteers")
            
            create_event_button = st.form_submit_button(label='Create Event')
        
        if create_event_button:
            if event_name and event_date and event_time and event_day and max_volunteers:
                events = load_data(EVENT_DATA_FILE)
                event_id = len(events) + 1
                event_data = {
                    'EventID': event_id,
                    'Event Name': event_name,
                    'Date': event_date,
                    'Time': event_time,
                    'Day': event_day,
                    'Max Volunteers': max_volunteers
                }
                save_data(EVENT_DATA_FILE, pd.concat([events, pd.DataFrame([event_data])], ignore_index=True))
                st.success("Event created successfully!")
            else:
                st.error("Please fill out all fields.")
    
    # View Registered Users tab
    with tabs[1]:
        st.subheader("Registered Users for Events")
        events = load_data(EVENT_DATA_FILE)
        registrations = load_data(REGISTRATION_DATA_FILE)
        users = load_data(USER_DATA_FILE)

        for _, event in events.iterrows():
            with st.expander(f"{event['Event Name']} on {event['Date']}"):
                registered_users = registrations[registrations['EventID'] == event['EventID']]['UserID']
                registered_users_data = users[users['ID'].isin(registered_users)]
                if registered_users_data.empty:
                    st.write("No registered users for this event.")
                else:
                    st.write(registered_users_data[['Name', 'Last Name', 'Mobile Number', 'Telegram ID', 'Username']])
    
    # Remove Event tab
    with tabs[2]:
        st.subheader("Remove Event")
        events = load_data(EVENT_DATA_FILE)
        event_to_remove = st.selectbox("Select Event to Remove", events['Event Name'])
        if st.button("Remove Event", key="remove_event_button"):
            event_id_to_remove = events[events['Event Name'] == event_to_remove].iloc[0]['EventID']
            events = events[events['EventID'] != event_id_to_remove]
            registrations = registrations[registrations['EventID'] != event_id_to_remove]
            save_data(EVENT_DATA_FILE, events)
            save_data(REGISTRATION_DATA_FILE, registrations)
            st.success(f"Event '{event_to_remove}' removed successfully!")
    
    if st.button("Logout", key="admin_logout_button"):
        st.session_state['logged_in'] = False
        st.session_state['page'] = 'login'
    
    if st.button("Back to Admin Panel", key="back_to_admin_panel_button"):
        st.session_state['page'] = 'admin_panel'



# User panel
# User panel
# User panel
def user_panel():
    st.title("User Panel")
    
    if 'username' not in st.session_state:
        st.error("User not logged in. Please log in.")
        return
    
    username = st.session_state['username']
    users = load_data(USER_DATA_FILE)
    user_id = users[users['Username'] == username].iloc[0]['ID']
    
    tabs = st.tabs(["Available Events", "Your Registered Events"])
    
    # Available Events tab
    with tabs[0]:
        st.subheader("Available Events")
        events = load_data(EVENT_DATA_FILE)
        registrations = load_data(REGISTRATION_DATA_FILE)
        
        for _, event in events.iterrows():
            with st.expander(f"{event['Event Name']} on {event['Date']}"):
                st.write(f"Max Volunteers: {event['Max Volunteers']}")
                registered_count = len(registrations[registrations['EventID'] == event['EventID']])
                if registered_count < event['Max Volunteers']:
                    if st.button(f"Register for {event['Event Name']}", key=f"register_{event['EventID']}"):
                        if not ((registrations['UserID'] == user_id) & (registrations['EventID'] == event['EventID'])).any():
                            registrations = pd.concat([registrations, pd.DataFrame([{'UserID': user_id, 'EventID': event['EventID']}])], ignore_index=True)
                            save_data(REGISTRATION_DATA_FILE, registrations)
                            st.success(f"Registered for {event['Event Name']}")
                        else:
                            st.error(f"You are already registered for {event['Event Name']}")
                else:
                    st.write("Event is full")
    
    # Registered Events tab
    with tabs[1]:
        st.subheader("Your Registered Events")
        user_registrations = registrations[registrations['UserID'] == user_id]
        user_events = events[events['EventID'].isin(user_registrations['EventID'])]
        
        for _, event in user_events.iterrows():
            with st.expander(f"{event['Event Name']} on {event['Date']}"):
                if st.button(f"Cancel Registration for {event['Event Name']}", key=f"cancel_{event['EventID']}"):
                    registrations = registrations[(registrations['UserID'] != user_id) | (registrations['EventID'] != event['EventID'])]
                    save_data(REGISTRATION_DATA_FILE, registrations)
                    st.success(f"Cancelled registration for {event['Event Name']}")
    
    if st.button("Logout", key="user_logout_button"):
        st.session_state['logged_in'] = False
        st.session_state['page'] = 'login'



# Main app logic
# Main app logic
# Main app logic
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'is_admin' not in st.session_state:
    st.session_state['is_admin'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ''
if 'page' not in st.session_state:
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


