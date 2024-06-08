import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64
import binascii

# File paths
USER_DATA_FILE = 'users.csv'
EVENT_DATA_FILE = 'events.csv'
REGISTRATION_DATA_FILE = 'registrations.csv'
MESSAGES_DATA_FILE = 'messages.csv'
FILES_DATA_FILE = 'files.csv'
CONTACT_DATA_FILE = 'contact_data.csv'

# Ensure files exist
for file in [USER_DATA_FILE, EVENT_DATA_FILE, REGISTRATION_DATA_FILE, MESSAGES_DATA_FILE, FILES_DATA_FILE, CONTACT_DATA_FILE]:
    if not os.path.exists(file):
        if file == USER_DATA_FILE:
            df = pd.DataFrame(columns=['ID', 'Name', 'Last Name', 'Mobile Number', 'Telegram ID', 'Username', 'Password'])
        elif file == EVENT_DATA_FILE:
            df = pd.DataFrame(columns=['EventID', 'Event Name', 'Date', 'Time', 'Day', 'Max Volunteers', 'Reserve Capacity'])
        elif file == REGISTRATION_DATA_FILE:
            df = pd.DataFrame(columns=['UserID', 'EventID', 'Status'])
        elif file == MESSAGES_DATA_FILE:
            df = pd.DataFrame(columns=(['UserID', 'Message', 'Response']))
        elif file == FILES_DATA_FILE:
            df = pd.DataFrame(columns=['UserID', 'Filename', 'FileData', 'FromAdmin'])
        elif file == CONTACT_DATA_FILE:
            df = pd.DataFrame(columns=(['UserID', 'Subject', 'Message']))
        df.to_csv(file, index=False)

def load_data(filename):
    data = pd.read_csv(filename)
    if 'FileData' in data.columns:
        def decode_filedata(x):
            try:
                return base64.b64decode(x.encode()) if pd.notnull(x) else None
            except (binascii.Error, ValueError) as e:
                st.error(f"Error decoding file data: {e}")
                return None

        data['FileData'] = data['FileData'].apply(decode_filedata)
    return data

def save_data(file, data):
    if file == FILES_DATA_FILE:
        data['FileData'] = data['FileData'].apply(lambda x: base64.b64encode(x).decode() if x is not None else None)
    data.to_csv(file, index=False)

# Other functions (check_credentials, username_exists, sign_up, login, logout, admin_panel, user_panel, main) remain the same

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
    st.title("Sign Up 📝")

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
    st.title("Login 🔐")

    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login", key="login_button"):
        if username == "admin" and password == "admin":
            st.session_state['logged_in'] = True
            st.session_state['is_admin'] = True
            st.session_state['username'] = "admin"  # Set username for admin
            st.session_state['page'] = 'admin_panel'
        elif check_credentials(username, password):
            st.session_state['logged_in'] = True
            st.session_state['is_admin'] = False
            st.session_state['username'] = username  # Set username for regular user
            st.session_state['page'] = 'user_panel'
        else:
            st.error("Invalid credentials")

    if st.button("Go to Sign Up", key="goto_signup_button"):
        st.session_state['page'] = 'sign_up'


def logout():
    if st.session_state.get('logged_in', False):
        if 'username' in st.session_state:
            st.session_state.pop('username')
        if 'role' in st.session_state:
            st.session_state.pop('role')
        st.session_state['logged_in'] = False
        st.rerun()  # Refresh the app to go to the login page

# Admin panel
def admin_panel():
    st.title("Admin Panel 🛠️")

    tabs = st.tabs(["Create Event 🎉", "View Registered Users 📋", "Remove Event ❌", "View All Users 👥", "User Messages ✉️", "File Exchange 📂"])

    # Create Event tab
    with tabs[0]:
        st.subheader("Create Event 🎉")
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
                st.success("Event created successfully! 🎉")
            else:
                st.error("Please fill out all fields.")

    # View Registered Users tab
    with tabs[1]:
        st.subheader("Registered Users for Events 📋")
        events = load_data(EVENT_DATA_FILE)
        registrations = load_data(REGISTRATION_DATA_FILE)
        users = load_data(USER_DATA_FILE)

        for _, event in events.iterrows():
            with st.expander(f"{event['Event Name']} on {event['Date']}"):
                main_list = registrations[(registrations['EventID'] == str(event['EventID'])) & (registrations['Status'] == 'Registered')]
                reserve_list = registrations[(registrations['EventID'] == str(event['EventID'])) & (registrations['Status'] == 'Reserve')]

                if not main_list.empty:
                    st.write("**Main List**")
                    main_list_users = pd.merge(main_list, users, left_on='UserID', right_on='ID', how='inner')
                    st.write(main_list_users[['Name', 'Last Name', 'Mobile Number', 'Telegram ID', 'Username']])

                if not reserve_list.empty:
                    st.write("**Reserve List**")
                    reserve_list_users = pd.merge(reserve_list, users, left_on='UserID', right_on='ID', how='inner')
                    st.write(reserve_list_users[['Name', 'Last Name', 'Mobile Number', 'Telegram ID', 'Username']])

    # Remove Event tab
    with tabs[2]:
        st.subheader("Remove Event ❌")
        events = load_data(EVENT_DATA_FILE)
        registrations = load_data(REGISTRATION_DATA_FILE)
        event_to_remove = st.selectbox("Select Event to Remove", events['Event Name'])
        if st.button("Remove Event"):
            event_id = events[events['Event Name'] == event_to_remove]['EventID'].values[0]
            events = events[events['EventID'] != event_id]
            registrations = registrations[registrations['EventID'] != str(event_id)]
            save_data(EVENT_DATA_FILE, events)
            save_data(REGISTRATION_DATA_FILE, registrations)
            st.success(f"Event '{event_to_remove}' removed successfully.")

    # View All Users tab
    with tabs[3]:
        st.subheader("All Users 👥")
        users = load_data(USER_DATA_FILE)
        st.write(users[['Name', 'Last Name', 'Mobile Number', 'Telegram ID', 'Username']])

    # User Messages tab
    with tabs[4]:
        st.subheader("User Messages ✉️")
        messages = load_data(MESSAGES_DATA_FILE)
        if messages.empty:
            st.write("No messages found.")
        else:
            users = load_data(USER_DATA_FILE)
            for _, message in messages.iterrows():
                user = users[users['ID'] == str(message['UserID'])].iloc[0]
                st.write(f"**From:** {user['Name']} {user['Last Name']} ({user['Username']})")
                st.write(f"**Message:** {message['Message']}")
                st.write(f"**Response:** {message['Response']}")
                st.write("---")

    # File Exchange tab
    with tabs[5]:
        st.subheader("File Exchange 📂")
        users = load_data(USER_DATA_FILE)
        files = load_data(FILES_DATA_FILE)

        # Files from users to admin
        user_files = files[files['FromAdmin'] == False]
        st.write("**Files from Users**")
        if not user_files.empty:
            for _, file in user_files.iterrows():
                user = users[users['ID'] == str(file['UserID'])].iloc[0]
                st.write(f"**From:** {user['Name']} {user['Last Name']} ({user['Username']})")
                st.download_button(label=f"Download {file['Filename']}", data=file['FileData'], file_name=file['Filename'])
                st.write("---")
        else:
            st.write("No files from users.")

        # Upload files to users
        st.write("**Send File to User**")
        user_select = st.selectbox("Select User", users['Username'])
        selected_user = users[users['Username'] == user_select].iloc[0]
        uploaded_file = st.file_uploader("Choose a file", key="admin_file_uploader")

        if st.button("Send File", key="send_file_button"):
            if uploaded_file:
                file_data = uploaded_file.read()
                file_entry = {
                    'UserID': str(selected_user['ID']),
                    'Filename': uploaded_file.name,
                    'FileData': file_data,
                    'FromAdmin': True
                }
                files = load_data(FILES_DATA_FILE)
                save_data(FILES_DATA_FILE, pd.concat([files, pd.DataFrame([file_entry])], ignore_index=True))
                st.success("File sent to user successfully.")
            else:
                st.error("Please upload a file.")

# User panel
def user_panel():
    st.title("User Panel")

    tabs = st.tabs(["Events", "My Registrations", "Messages", "Contact Admin", "Files"])

    # Events tab
    with tabs[0]:
        st.subheader("Available Events 🎉")
        events = load_data(EVENT_DATA_FILE)
        registrations = load_data(REGISTRATION_DATA_FILE)
        users = load_data(USER_DATA_FILE)
        current_user = users[users['Username'] == st.session_state['username']].iloc[0]

        for _, event in events.iterrows():
            with st.expander(f"{event['Event Name']} on {event['Date']}"):
                st.write(f"**Time:** {event['Time']}")
                st.write(f"**Day:** {event['Day']}")
                st.write(f"**Max Volunteers:** {event['Max Volunteers']}")
                st.write(f"**Reserve Capacity:** {event['Reserve Capacity']}")

                registered_users = registrations[registrations['EventID'] == str(event['EventID'])]
                num_registered = len(registered_users[registered_users['Status'] == 'Registered'])
                num_reserve = len(registered_users[registered_users['Status'] == 'Reserve'])

                if num_registered < event['Max Volunteers']:
                    if st.button(f"Register for {event['Event Name']}", key=f"register_{event['EventID']}"):
                        registrations = load_data(REGISTRATION_DATA_FILE)
                        new_registration = {
                            'UserID': str(current_user['ID']),
                            'EventID': str(event['EventID']),
                            'Status': 'Registered'
                        }
                        save_data(REGISTRATION_DATA_FILE, pd.concat([registrations, pd.DataFrame([new_registration])], ignore_index=True))
                        st.success(f"Registered for {event['Event Name']}.")
                elif num_reserve < event['Reserve Capacity']:
                    if st.button(f"Register for Reserve List for {event['Event Name']}", key=f"reserve_{event['EventID']}"):
                        registrations = load_data(REGISTRATION_DATA_FILE)
                        new_registration = {
                            'UserID': str(current_user['ID']),
                            'EventID': str(event['EventID']),
                            'Status': 'Reserve'
                        }
                        save_data(REGISTRATION_DATA_FILE, pd.concat([registrations, pd.DataFrame([new_registration])], ignore_index=True))
                        st.success(f"Registered for Reserve List for {event['Event Name']}.")
                else:
                    st.write("No spots available.")

    # My Registrations tab
    with tabs[1]:
        st.subheader("My Registrations 📋")
        registrations = load_data(REGISTRATION_DATA_FILE)
        events = load_data(EVENT_DATA_FILE)
        users = load_data(USER_DATA_FILE)
        current_user = users[users['Username'] == st.session_state['username']].iloc[0]

        user_registrations = registrations[registrations['UserID'] == str(current_user['ID'])]
        if not user_registrations.empty:
            for _, reg in user_registrations.iterrows():
                event = events[events['EventID'] == int(reg['EventID'])].iloc[0]
                st.write(f"**Event:** {event['Event Name']}")
                st.write(f"**Date:** {event['Date']}")
                st.write(f"**Status:** {reg['Status']}")
                st.write("---")
        else:
            st.write("No registrations found.")

    # Messages tab
    with tabs[2]:
        st.subheader("Messages ✉️")
        users = load_data(USER_DATA_FILE)
        messages = load_data(MESSAGES_DATA_FILE)
        current_user = users[users['Username'] == st.session_state['username']].iloc[0]

        user_messages = messages[messages['UserID'] == str(current_user['ID'])]
        if user_messages.empty:
            st.write("No messages found.")
        else:
            for _, message in user_messages.iterrows():
                st.write(f"**Message:** {message['Message']}")
                st.write(f"**Response:** {message['Response']}")
                st.write("---")

    # Contact Admin tab
    with tabs[3]:
        st.subheader("Contact Admin ✉️")
        with st.form(key='contact_admin_form'):
            subject = st.text_input("Subject", key="contact_subject")
            message = st.text_area("Message", key="contact_message")

            send_message_button = st.form_submit_button(label='Send Message')

        if send_message_button:
            if subject and message:
                users = load_data(USER_DATA_FILE)
                current_user = users[users['Username'] == st.session_state['username']].iloc[0]
                contact_data = load_data(CONTACT_DATA_FILE)
                new_message = {
                    'UserID': str(current_user['ID']),
                    'Subject': subject,
                    'Message': message
                }
                save_data(CONTACT_DATA_FILE, pd.concat([contact_data, pd.DataFrame([new_message])], ignore_index=True))
                st.success("Message sent to admin successfully.")
            else:
                st.error("Please fill out all fields.")

    # Files tab
    with tabs[4]:
        st.subheader("Files 📂")
        users = load_data(USER_DATA_FILE)
        files = load_data(FILES_DATA_FILE)
        current_user = users[users['Username'] == st.session_state['username']].iloc[0]

        # Upload file to admin
        st.write("**Upload File to Admin**")
        uploaded_file = st.file_uploader("Choose a file", key="user_file_uploader")

        if st.button("Upload File", key="upload_file_button"):
            if uploaded_file:
                file_data = uploaded_file.read()
                file_entry = {
                    'UserID': str(current_user['ID']),
                    'Filename': uploaded_file.name,
                    'FileData': file_data,
                    'FromAdmin': False
                }
                files = load_data(FILES_DATA_FILE)
                save_data(FILES_DATA_FILE, pd.concat([files, pd.DataFrame([file_entry])], ignore_index=True))
                st.success("File uploaded successfully.")
            else:
                st.error("Please upload a file.")

        # Files from admin
        admin_files = files[(files['UserID'] == str(current_user['ID'])) & (files['FromAdmin'] == True)]
        st.write("**Files from Admin**")
        if not admin_files.empty:
            for _, file in admin_files.iterrows():
                st.download_button(label=f"Download {file['Filename']}", data=file['FileData'], file_name=file['Filename'])
                st.write("---")
        else:
            st.write("No files from admin.")

# Main function to
def main():
    st.set_page_config(page_title="Events and Games", page_icon="🌟")

    # Custom CSS to style elements
    st.markdown(
        """
        <style>
        .stButton>button {
            background-color: #4CAF50; /* Green */
            border: none;
            color: white;
            padding: 15px 32px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 12px;
        }
        .stTextInput>div>input {
            border-radius: 12px;
            border: 2px solid #4CAF50;
            padding: 10px;
            font-size: 16px;
        }
        .stTextArea>div>textarea {
            border-radius: 12px;
            border: 2px solid #4CAF50;
            padding: 10px;
            font-size: 16px;
        }
        .stDateInput>div>input {
            border-radius: 12px;
            border: 2px solid #4CAF50;
            padding: 10px;
            font-size: 16px;
        }
        .stTimeInput>div>input {
            border-radius: 12px;
            border: 2px solid #4CAF50;
            padding: 10px;
            font-size: 16px;
        }
        .stNumberInput>div>input {
            border-radius: 12px;
            border: 2px solid #4CAF50;
            padding: 10px;
            font-size: 16px;
        }
        .stSelectbox>div>select {
            border-radius: 12px;
            border: 2px solid #4CAF50;
            padding: 10px;
            font-size: 16px;
        }
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
            color: #4CAF50;
        }
        </style>
        """, unsafe_allow_html=True
    )

    if 'page' not in st.session_state:
        st.session_state['page'] = 'login'
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'is_admin' not in st.session_state:
        st.session_state['is_admin'] = False

    if st.session_state['page'] == 'login':
        login()
    elif st.session_state['page'] == 'sign_up':
        sign_up()
    elif st.session_state['page'] == 'user_panel' and st.session_state['logged_in']:
        user_panel()
    elif st.session_state['page'] == 'admin_panel' and st.session_state['logged_in'] and st.session_state['is_admin']:
        admin_panel()
    else:
        st.session_state['page'] = 'login'
        login()

    if st.session_state.get('logged_in', False):
        st.sidebar.title("Navigation 🧭")
        if st.button("Logout", key="logout_button"):
            logout()

if __name__ == "__main__":
    main()

