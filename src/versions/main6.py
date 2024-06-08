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
    if 'Reserve Capacity' in data.columns:
        data['Reserve Capacity'] = pd.to_numeric(data['Reserve Capacity'], errors='coerce')
        # Handle NaN values if necessary
        # data['Reserve Capacity'].fillna(0, inplace=True)  # Example: Replace NaN with 0
        data['Reserve Capacity'] = data['Reserve Capacity'].astype(pd.Int64Dtype(), errors='ignore')
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
                registered_users = registrations[registrations['EventID'] == event['EventID']]['UserID']
                registered_users_data = users[users['ID'].isin(registered_users)]
                if registered_users_data.empty:
                    st.write("No registered users for this event.")
                else:
                    for index, user in registered_users_data.iterrows():
                        cancel_button_clicked = st.button(f"Cancel Registration for {user['Name']} {user['Last Name']}")
                        if cancel_button_clicked:
                            # Remove the registration
                            registrations = registrations.drop(registrations[(registrations['UserID'] == user['ID']) & (registrations['EventID'] == event['EventID'])].index)
                            save_data(REGISTRATION_DATA_FILE, registrations)
                            st.success(f"Registration for {user['Name']} {user['Last Name']} canceled successfully!")

                            # Reload the registered users data and update the displayed list
                            registered_users = registrations[registrations['EventID'] == event['EventID']]['UserID']
                            registered_users_data = users[users['ID'].isin(registered_users)]

                    if not registered_users_data.empty:
                        st.write(registered_users_data[['Name', 'Last Name', 'Mobile Number', 'Telegram ID', 'Username']])

        # Download button for all registered users
        all_registered_users = pd.concat([users[users['ID'].isin(registrations['UserID'])], registrations], axis=1)
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
            save_data(EVENT_DATA_FILE, events)
            registrations = registrations[registrations['EventID'] != event_id_to_remove]
            save_data(REGISTRATION_DATA_FILE, registrations)
            st.success("Event removed successfully!")

    # View All Users tab
    with tabs[3]:
        st.subheader("All Users")
        users = load_data(USER_DATA_FILE)
        if users.empty:
            st.write("No users registered.")
        else:
            st.write(users[['Name', 'Last Name', 'Mobile Number', 'Telegram ID', 'Username']])

    # User Messages tab
    with tabs[4]:
        st.subheader("User Messages")
        messages = load_data(MESSAGES_DATA_FILE)
        users = load_data(USER_DATA_FILE)

        if messages.empty:
            st.write("No messages from users.")
        else:
            for _, message in messages.iterrows():
                user = users[users['ID'] == message['UserID']].iloc[0]
                st.write(f"Message from {user['Name']} {user['Last Name']} ({user['Username']}):")
                st.write(message['Message'])
                response = st.text_area("Response", key=f"response_{message['UserID']}_{message['Message']}")
                if st.button("Send Response", key=f"send_response_{message['UserID']}_{message['Message']}"):
                    messages.at[message.name, 'Response'] = response
                    save_data(MESSAGES_DATA_FILE, messages)
                    st.success("Response sent successfully!")

# User panel
def user_panel():
    st.title("User Panel")

    events = load_data(EVENT_DATA_FILE)
    registrations = load_data(REGISTRATION_DATA_FILE)
    users = load_data(USER_DATA_FILE)
    username = st.session_state['username']
    user_id = users[users['Username'] == username].iloc[0]['ID']

    with st.form(key='register_event_form'):
        st.subheader("Available Events")
        st.dataframe(events)

        event_id = st.text_input("Enter Event ID to Register", key="register_event_id")
        register_button = st.form_submit_button(label='Register for Event')

    if register_button:
        if not event_id:
            st.error("Please enter an Event ID.")
        else:
            event = events[events['EventID'] == int(event_id)]
            if event.empty:
                st.error("Invalid Event ID.")
            else:
                event = event.iloc[0]
                if len(registrations[registrations['EventID'] == event['EventID']]) < event['Max Volunteers'] + event['Reserve Capacity']:
                    if registrations[(registrations['UserID'] == user_id) & (registrations['EventID'] == event['EventID'])].empty:
                        new_registration = {'UserID': user_id, 'EventID': event['EventID'], 'Status': 'registered'}
                        registrations = pd.concat([registrations, pd.DataFrame([new_registration])], ignore_index=True)
                        save_data(REGISTRATION_DATA_FILE, registrations)
                        st.success(f"Successfully registered for {event['Event Name']}!")
                    else:
                        st.error("You are already registered for this event.")
                else:
                    st.error("Event is fully booked.")

    # View My Registrations
    st.subheader("My Registrations")
    user_registrations = registrations[registrations['UserID'] == user_id]
    if user_registrations.empty:
        st.write("You have no registrations.")
    else:
        for _, reg in user_registrations.iterrows():
            event = events[events['EventID'] == reg['EventID']].iloc[0]
            st.write(f"Event Name: {event['Event Name']}, Date: {event['Date']}, Time: {event['Time']}, Status: {reg['Status']}")
            if st.button(f"Cancel Registration for {event['Event Name']}", key=f"cancel_{event['EventID']}"):
                registrations = registrations.drop(reg.name)
                save_data(REGISTRATION_DATA_FILE, registrations)
                st.success(f"Canceled registration for {event['Event Name']}")

    # Contact Admin
    st.subheader("Contact Admin")
    with st.form(key='contact_form'):
        message = st.text_area("Message", key="user_message")
        send_message_button = st.form_submit_button(label='Send Message')
    if send_message_button:
        if not message:
            st.error("Please enter a message.")
        else:
            messages = load_data(MESSAGES_DATA_FILE)
            new_message = {'UserID': user_id, 'Message': message, 'Response': ''}
            messages = pd.concat([messages, pd.DataFrame([new_message])], ignore_index=True)
            save_data(MESSAGES_DATA_FILE, messages)
            st.success("Message sent to admin successfully!")

# Main code
def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['is_admin'] = False

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

if __name__ == "__main__":
    main()

