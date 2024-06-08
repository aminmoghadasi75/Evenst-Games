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
    # View Registered Users tab
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
                            st.experimental_rerun()
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
            registrations = registrations[registrations['EventID'] != event_id_to_remove]
            save_data(EVENT_DATA_FILE, events)
            save_data(REGISTRATION_DATA_FILE, registrations)
            st.success(f"Event '{event_to_remove}' removed successfully!")

        # Download button for events
        if not events.empty:
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                events.to_excel(writer, index=False, sheet_name='Events')
                writer.close()
            st.download_button(
                label="Download Events as Excel",
                data=buffer,
                file_name="events.xlsx",
                mime="application/vnd.ms-excel"
            )

    # View All Users tab
    with tabs[3]:
        st.subheader("All Users Information")
        users = load_data(USER_DATA_FILE)
        if users.empty:
            st.write("No users found.")
        else:
            st.dataframe(users)

            # Download button for all users
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                                users.to_excel(writer, index=False, sheet_name='Users')
                                writer.close()
            st.download_button(
                label="Download Users as Excel",
                data=buffer,
                file_name="users.xlsx",
                mime="application/vnd.ms-excel"
            )

    # Contact Us tab
    with tabs[4]:
        st.subheader("User Messages")
        messages = load_data(MESSAGES_DATA_FILE)

        # Display user messages and responses
        st.subheader("Users' Messages and Responses")
        if messages.empty:
            st.write("No messages found.")
        else:
            for _, user_message in messages.iterrows():
                st.write(f"User ID: {user_message['UserID']}")
                st.write(f"Message: {user_message['Message']}")
                st.write(f"Response: {user_message['Response']}")

        # Form for responding to user messages
        with st.form(key='response_form'):
            user_id = st.text_input("User ID", key="response_user_id")
            message = st.text_area("User's Message", key="user_message", disabled=True)
            response = st.text_area("Your Response", key="response_message")
            submit_button = st.form_submit_button(label='Send Response')

        if submit_button:
            if response:
                # Update the messages dataframe with the admin response
                messages.loc[messages['UserID'] == user_id, 'Response'] = response
                save_data(MESSAGES_DATA_FILE, messages)
                st.success("Response sent successfully!")
            else:
                st.error("Please enter a response.")

    if st.button("Logout", key="admin_logout_button"):
        st.session_state['logged_in'] = False
        st.session_state['page'] = 'login'
# User panel
# User panel
def user_panel():
    st.title("User Panel")

    tabs = st.tabs(["View Events", "Register for Event", "Cancel Registration", "Contact Us"])  # Added "Contact Us" tab

    # Define user_id variable
    user_id = st.session_state.get('username', '')

    # View Events tab
    with tabs[0]:
        st.subheader("Available Events")
        events = load_data(EVENT_DATA_FILE)
        if events.empty:
            st.write("No events available.")
        else:
            st.dataframe(events)

            # Download button for events
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                events.to_excel(writer, index=False, sheet_name='Events')
                writer.close()
            st.download_button(
                label="Download Events as Excel",
                data=buffer,
                file_name="events.xlsx",
                mime="application/vnd.ms-excel"
            )

    # Register for Event tab
    # Register for Event tab
    with tabs[1]:
        st.subheader("Register for an Event")
        events = load_data(EVENT_DATA_FILE)
        users = load_data(USER_DATA_FILE)
        registrations = load_data(REGISTRATION_DATA_FILE)

        event_to_register = st.selectbox("Select Event", events['Event Name'])
        if st.button("Register", key="register_button"):
            if user_id:  # Check if user_id is not empty
                event_id = events[events['Event Name'] == event_to_register]['EventID'].values[0]
                registered_users_count = len(registrations[registrations['EventID'] == event_id])

                # Check if the event has reached its maximum capacity
                if registered_users_count < events[events['EventID'] == event_id]['Max Volunteers'].values[0]:
                    status = 'Registered'
                else:
                    status = 'Reserve'

                if registrations[(registrations['UserID'] == user_id) & (registrations['EventID'] == event_id)].empty:
                    new_registration = pd.DataFrame([{'UserID': user_id, 'EventID': event_id, 'Status': status}])
                    registrations = pd.concat([registrations, new_registration], ignore_index=True)
                    save_data(REGISTRATION_DATA_FILE, registrations)
                    st.success(f"Registered for event '{event_to_register}' successfully! You are in the {status} list.")
                else:
                    st.warning("You are already registered for this event.")

    # Cancel Registration tab
    with tabs[2]:
        st.subheader("Cancel Registration")

        events = load_data(EVENT_DATA_FILE)
        registrations = load_data(REGISTRATION_DATA_FILE)

        user_registrations = registrations[registrations['UserID'] == user_id]

        if user_registrations.empty:
            st.write("You are not registered for any events.")
        else:
            for index, row in user_registrations.iterrows():
                event_details = events[events['EventID'] == row['EventID']].iloc[0]
                st.write(f"Event: {event_details['Event Name']}")
                st.write(f"Date: {event_details['Date']}")
                st.write(f"Time: {event_details['Time']}")
                st.write(f"Day: {event_details['Day']}")
                st.write(f"Status: {row['Status']}")

                if st.button(f"Cancel Registration for {event_details['Event Name']}", key=f"cancel_registration_{index}"):
                    # Remove registration
                    registrations = registrations.drop(index)
                    save_data(REGISTRATION_DATA_FILE, registrations)
                    st.success("Registration canceled successfully!")

                    # Check if there are users in the reserve list for this event
                    reserve_list = registrations[(registrations['EventID'] == row['EventID']) & (registrations['Status'] == 'Reserve')]
                    if not reserve_list.empty:
                        # Replace the first person in the reserve list with the canceled user
                        first_reserve_user = reserve_list.iloc[0]
                        registrations.loc[first_reserve_user.name, 'Status'] = 'Registered'
                        save_data(REGISTRATION_DATA_FILE, registrations)
                        st.info(f"The first person in the reserve list has been moved to registered for '{event_details['Event Name']}'.")



    # Contact Us tab
    with tabs[3]:
        st.subheader("Contact Us")
        telegram_link = "[Contact us on Telegram](https://t.me/amin_moghadasi)"
        st.markdown(telegram_link, unsafe_allow_html=True)

        with st.form(key='contact_form'):
            message = st.text_area("Your message")
            submit_button = st.form_submit_button(label='Send Message')

        if submit_button:
            if message:
                messages = load_data(MESSAGES_DATA_FILE)
                new_message = pd.DataFrame([{'UserID': user_id, 'Message': message, 'Response': ''}])
                messages = pd.concat([messages, new_message], ignore_index=True)
                save_data(MESSAGES_DATA_FILE, messages)
                st.success("Message sent successfully!")
            else:
                st.error("Please enter a message.")

        # Display user messages and responses
        st.subheader("Your Messages and Responses")
        messages = load_data(MESSAGES_DATA_FILE)
        user_messages = messages[messages['UserID'] == user_id]
        if user_messages.empty:
            st.write("No messages found.")
        else:
            for _, user_message in user_messages.iterrows():
                st.write(f"Message: {user_message['Message']}")
                st.write(f"Response: {user_message['Response']}")

    if st.button("Logout", key="user_logout_button"):
        st.session_state['logged_in'] = False
        st.session_state['page'] = 'login'


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

