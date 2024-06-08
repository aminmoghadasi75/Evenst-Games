import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import BytesIO

# File paths
USER_DATA_FILE = 'users.csv'
EVENT_DATA_FILE = 'events.csv'
REGISTRATION_DATA_FILE = 'registrations.csv'
MESSAGES_DATA_FILE = 'messages.csv'

# Ensure files exist
for file in [USER_DATA_FILE, EVENT_DATA_FILE, REGISTRATION_DATA_FILE, MESSAGES_DATA_FILE]:
    if not os.path.exists(file):
        if file == USER_DATA_FILE:
            df = pd.DataFrame(columns=['ID', 'Name', 'Last Name', 'Mobile Number', 'Telegram ID', 'Username', 'Password'])
        elif file == EVENT_DATA_FILE:
            df = pd.DataFrame(columns=['EventID', 'Event Name', 'Date', 'Time', 'Day', 'Max Volunteers', 'Reserve Capacity'])
        elif file == REGISTRATION_DATA_FILE:
            df = pd.DataFrame(columns=['UserID', 'EventID', 'Status'])
        elif file == MESSAGES_DATA_FILE:
            df = pd.DataFrame(columns=['UserID', 'Message', 'Response'])
        df.to_csv(file, index=False)

# Utility functions
def load_data(file):
    data = pd.read_csv(file, dtype='str')
    for column in data.columns:
        if data[column].dtype == 'object':
            data[column] = data[column].str.strip()
    if 'Max Volunteers' in data.columns:
        data['Max Volunteers'] = data['Max Volunteers'].astype(int)
    if 'Status' in data.columns:
        data['Status'] = data['Status'].astype(str)
    return data

def save_data(file, data):
    data.to_csv(file, index=False)

# Check credentials
def check_credentials(username, password):
    users = load_data(USER_DATA_FILE)
    user = users[users['Username'] == username]
    if not user.empty:
        stored_password = user.iloc[0]['Password']
        return stored_password == password
    return False

# Check if username exists
def username_exists(username):
    users = load_data(USER_DATA_FILE)
    return username in users['Username'].values

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
def admin_panel():
    st.title("Admin Panel")

    tabs = st.tabs(["Create Event", "View Registered Users", "Remove Event", "View All Users", "User Messages"])  # Added "Contact Us" tab

    # Create Event tab
    with tabs[0]:
        st.subheader("Create Event")
        with st.form(key='create_event_form'):
            event_name = st.text_input("Event Name", key="event_name")
            event_date = st.date_input("Event Date", key="event_date", min_value=datetime.today())
            event_time = st.time_input("Event Time", key="event_time")
            event_day = st.selectbox("Event Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], key="event_day")
            max_volunteers = st.number_input("Max Volunteers", min_value=1, step=1, key="max_volunteers")
            reserve_capacity = st.number_input("Reserve Capacity", min_value=1, step=1, key="reserve_capacity")

            create_event_button = st.form_submit_button(label='Create Event')

        if create_event_button:
            if event_name and event_date and event_time and event_day and max_volunteers and reserve_capacity:
                events = load_data(EVENT_DATA_FILE)
                event_id = len(events) + 1
                event_data = {
                    'EventID': event_id,
                    'Event Name': event_name,
                    'Date': event_date,
                    'Time': event_time,
                    'Day': event_day,
                    'Max Volunteers': max_volunteers,
                    'Reserve Capacity': reserve_capacity
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
                registered_users = registrations[registrations['EventID'] == str(event['EventID'])]['UserID']
                registered_users_data = users[users['ID'].isin(registered_users)]
                if registered_users_data.empty:
                    st.write("No registered users for this event.")
                else:
                    for index, user in registered_users_data.iterrows():
                        cancel_button_clicked = st.button(f"Cancel Registration for {user['Name']} {user['Last Name']}", key=f"cancel_{user['ID']}_{event['EventID']}")
                        if cancel_button_clicked:
                            # Remove the registration
                            registrations = registrations.drop(registrations[(registrations['UserID'] == user['ID']) & (registrations['EventID'] == str(event['EventID']) )].index)
                            save_data(REGISTRATION_DATA_FILE, registrations)
                            st.success(f"Registration for {user['Name']} {user['Last Name']} canceled successfully!")
                            st.experimental_rerun()
                    if not registered_users_data.empty:
                        st.write(registered_users_data[['Name', 'Last Name', 'Mobile Number', 'Telegram ID', 'Username']])

        # Download button for all registered users
        all_registered_users = pd.merge(users, registrations, left_on='ID', right_on='UserID')
        if not all_registered_users.empty:
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                all_registered_users.to_excel(writer, index=False, sheet_name='Registered Users')
                writer.close()
            st.download_button(
                label="Download Registered Users as Excel",
                data=buffer,
                file_name="registered_users.xlsx",
                mime="application/vnd.ms-excel"
            )


    # Remove Event tab
    with tabs[2]:
        st.subheader("Remove Event")
        events = load_data(EVENT_DATA_FILE)
        registrations = load_data(REGISTRATION_DATA_FILE)
        event_to_remove = st.selectbox("Select Event to Remove", events['Event Name'])
        if st.button("Remove Event", key="remove_event_button"):
            event_id_to_remove = events[events['Event Name'] == event_to_remove].iloc[0]['EventID']
            events = events[events['EventID'] != event_id_to_remove]
            registrations = registrations[registrations['EventID'] != event_id_to_remove]
            save_data(EVENT_DATA_FILE, events)
            save_data(REGISTRATION_DATA_FILE, registrations)
            st.success("Event removed successfully!")

    # View All Users tab
    with tabs[3]:
        st.subheader("All Users")
        users = load_data(USER_DATA_FILE)
        st.write(users[['ID', 'Name', 'Last Name', 'Mobile Number', 'Telegram ID', 'Username']])

    # User Messages tab
    with tabs[4]:
        st.subheader("Messages from Users")
        messages = load_data(MESSAGES_DATA_FILE)
        users = load_data(USER_DATA_FILE)
        for index, message in messages.iterrows():
            user = users[users['ID'] == message['UserID']].iloc[0]
            with st.expander(f"Message from {user['Name']} {user['Last Name']} ({user['Username']})"):
                st.write(message['Message'])
                response = st.text_area("Response", key=f"response_{index}")
                if st.button("Send Response", key=f"send_response_{index}"):
                    messages.at[index, 'Response'] = response
                    save_data(MESSAGES_DATA_FILE, messages)
                    st.success("Response sent successfully!")

    if st.button("Logout", key="admin_logout_button"):
        st.session_state['logged_in'] = False
        st.session_state['is_admin'] = False
        st.session_state['page'] = 'login'

# User panel
# User panel
def user_panel():
    st.title("User Panel")

    username = st.session_state.get('username')
    users = load_data(USER_DATA_FILE)
    user = users[users['Username'] == username]

    if user.empty:
        st.error("User not found. Please log in again.")
        st.session_state['logged_in'] = False
        st.session_state['username'] = None
        st.session_state['page'] = 'login'
        return

    user = user.iloc[0]

    if st.button("Logout", key="user_logout_button"):
        st.session_state['logged_in'] = False
        st.session_state['username'] = None
        st.session_state['page'] = 'login'

    events = load_data(EVENT_DATA_FILE)
    registrations = load_data(REGISTRATION_DATA_FILE)
    user_registrations = registrations[registrations['UserID'] == str(user['ID'])]

    # Register for Events
    st.subheader("Register for Events")
    for _, event in events.iterrows():
        if str(event['EventID']) not in user_registrations['EventID'].values:
            st.write(f"{event['Event Name']} on {event['Date']} at {event['Time']}")
            if st.button(f"Register for {event['Event Name']}", key=f"register_{event['EventID']}"):
                registrations = load_data(REGISTRATION_DATA_FILE)  # Reload data to avoid conflicts
                if (registrations['EventID'] == str(event['EventID'])).sum() < event['Max Volunteers']:
                    registration_data = {'UserID': str(user['ID']), 'EventID': str(event['EventID']), 'Status': 'Registered'}
                    registrations = pd.concat([registrations, pd.DataFrame([registration_data])], ignore_index=True)
                    save_data(REGISTRATION_DATA_FILE, registrations)
                    st.success(f"Successfully registered for {event['Event Name']}!")
                    st.experimental_rerun()

    # View Registered Events
    st.subheader("Registered Events")
    for _, registration in user_registrations.iterrows():
        event = events[events['EventID'] == str(registration['EventID'])].iloc[0]
        st.write(f"{event['Event Name']} on {event['Date']} at {event['Time']}")
        if st.button(f"Cancel Registration for {event['Event Name']}", key=f"cancel_registration_{event['EventID']}"):
            registrations = registrations.drop(registrations[(registrations['UserID'] == str(user['ID'])) & (registrations['EventID'] == str(event['EventID']))].index)
            save_data(REGISTRATION_DATA_FILE, registrations)
            st.success(f"Registration for {event['Event Name']} canceled successfully!")
            st.experimental_rerun()

    # Contact Us
    st.subheader("Contact Us")
    message = st.text_area("Write your message here")
    if st.button("Send Message", key="send_message_button"):
        messages = load_data(MESSAGES_DATA_FILE)
        message_data = {'UserID': str(user['ID']), 'Message': message, 'Response': ''}
        save_data(MESSAGES_DATA_FILE, pd.concat([messages, pd.DataFrame([message_data])], ignore_index=True))
        st.success("Message sent successfully!")

# Main app logic
def main():
    if 'page' not in st.session_state:
        st.session_state['page'] = 'login'

    if st.session_state['page'] == 'login':
        login()
    elif st.session_state['page'] == 'sign_up':
        sign_up()
    elif st.session_state['page'] == 'admin_panel' and st.session_state.get('is_admin', False):
        admin_panel()
    elif st.session_state['page'] == 'user_panel' and st.session_state.get('logged_in', False):
        user_panel()
    else:
        st.session_state['page'] = 'login'
        login()

if __name__ == "__main__":
    main()
