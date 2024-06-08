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
FILES_DATA_FILE = 'files.csv'

# Ensure files exist
for file in [USER_DATA_FILE, EVENT_DATA_FILE, REGISTRATION_DATA_FILE, MESSAGES_DATA_FILE, FILES_DATA_FILE]:
    if not os.path.exists(file):
        if file == USER_DATA_FILE:
            df = pd.DataFrame(columns=['ID', 'Name', 'Last Name', 'Mobile Number', 'Telegram ID', 'Username', 'Password'])
        elif file == EVENT_DATA_FILE:
            df = pd.DataFrame(columns=['EventID', 'Event Name', 'Date', 'Time', 'Day', 'Max Volunteers', 'Reserve Capacity'])
        elif file == REGISTRATION_DATA_FILE:
            df = pd.DataFrame(columns=['UserID', 'EventID', 'Status'])
        elif file == MESSAGES_DATA_FILE:
            df = pd.DataFrame(columns=['UserID', 'Message', 'Response'])
        elif file == FILES_DATA_FILE:
            df = pd.DataFrame(columns=['UserID', 'Filename', 'FileData', 'FromAdmin'])
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

    tabs = st.tabs(["Create Event", "View Registered Users", "Remove Event", "View All Users", "User Messages", "File Exchange"])

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
            user_info = users[users['ID'] == message['UserID']]
            if not user_info.empty:
                user_info = user_info.iloc[0]
                st.write(f"**From:** {user_info['Name']} {user_info['Last Name']} ({user_info['Username']})")
                st.write(f"**Message:** {message['Message']}")
                response = st.text_area(f"Response to {user_info['Username']}", key=f"response_{index}")
                if st.button(f"Send Response", key=f"send_response_{index}"):
                    messages.at[index, 'Response'] = response
                    save_data(MESSAGES_DATA_FILE, messages)
                    st.success("Response sent!")

    # File Exchange tab
    # File Exchange tab (Admin Panel)
    # File Exchange tab (Admin Panel)
    # File Exchange tab (Admin Panel)
    # File Exchange tab (Admin Panel)
    # File Exchange tab (Admin Panel)
    # File Exchange tab (Admin Panel)
    with tabs[5]:
        st.subheader("File Exchange")
        
        st.write("**Files from Users**")
        files = load_data(FILES_DATA_FILE)
        users = load_data(USER_DATA_FILE)
        
        user_files = files[files['FromAdmin'] == 'False']  # Ensure 'False' is treated as a string
        for index, file in user_files.iterrows():
            user_info = users[users['ID'] == file['UserID']]
            if not user_info.empty:
                user_info = user_info.iloc[0]
                st.write(f"**From:** {user_info['Name']} {user_info['Last Name']} ({user_info['Username']})")
                st.write(f"**Filename:** {file['Filename']}")
                st.download_button(
                    "Download", 
                    data=BytesIO(bytes(eval(file['FileData']))), 
                    file_name=file['Filename'],
                    key=f"download_user_{index}"  # Unique key for each button
                )
        
        st.write("**Upload File for Users**")
        uploaded_file = st.file_uploader("Choose a file")
        if uploaded_file is not None:
            users = load_data(USER_DATA_FILE)
            user_to_send = st.selectbox("Select User to Send", users['Username'])
            if st.button("Upload and Send"):
                user_id_to_send = users[users['Username'] == user_to_send].iloc[0]['ID']
                file_data = uploaded_file.getvalue()
                new_file = {
                    'UserID': user_id_to_send,
                    'Filename': uploaded_file.name,
                    'FileData': str(list(file_data)),  # Convert bytes to list of integers and store as string
                    'FromAdmin': 'True'
                }
                files = pd.concat([files, pd.DataFrame([new_file])], ignore_index=True)
                save_data(FILES_DATA_FILE, files)
                st.success("File sent successfully!")




# User panel
def user_panel():
    st.title("User Panel")

    tabs = st.tabs(["Events", "My Registrations", "Contact Us", "File Exchange"])

    events = load_data(EVENT_DATA_FILE)  # Ensure events are loaded
    registrations = load_data(REGISTRATION_DATA_FILE)  # Ensure registrations are loaded
    users = load_data(USER_DATA_FILE)  # Ensure users are loaded
    user_id = users[users['Username'] == st.session_state['username']].iloc[0]['ID']
    user_registrations = registrations[registrations['UserID'] == user_id]
    
    # Register for Events tab
    with tabs[0]:
        st.subheader("Register for Events")
        for _, event in events.iterrows():
            event_id = str(event['EventID'])
            main_list_count = len(registrations[(registrations['EventID'] == event_id) & (registrations['Status'] == 'Registered')])
            reserve_list_count = len(registrations[(registrations['EventID'] == event_id) & (registrations['Status'] == 'Reserve')])

            reserve_capacity = int(event['Reserve Capacity'])

            if main_list_count < event['Max Volunteers']:
                register_status = 'Registered'
            elif reserve_list_count < reserve_capacity:
                register_status = 'Reserve'
            else:
                register_status = None

            if event_id not in user_registrations['EventID'].values and register_status:
                with st.container():
                    st.markdown(f"""
                    <div class="event-box">
                        <div class="event-title">{event['Event Name']}</div>
                        <div>Date: {event['Date']}</div>
                        <div>Time: {event['Time']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Register for {event['Event Name']}", key=f"register_{event_id}", help="Register for this event"):
                        registrations = load_data(REGISTRATION_DATA_FILE)  # Reload data to avoid conflicts
                        registration_data = {'UserID': str(user_id), 'EventID': event_id, 'Status': register_status}
                        registrations = pd.concat([registrations, pd.DataFrame([registration_data])], ignore_index=True)
                        save_data(REGISTRATION_DATA_FILE, registrations)
                        if register_status == 'Registered':
                            st.success(f"Successfully registered for {event['Event Name']}!")
                        else:
                            st.warning(f"Event is full. You have been added to the reserve list for {event['Event Name']}.")
                        st.experimental_rerun()



    # My Registrations tab
    with tabs[1]:
        st.subheader("My Registrations")
        users = load_data(USER_DATA_FILE)
        registrations = load_data(REGISTRATION_DATA_FILE)
        events = load_data(EVENT_DATA_FILE)
        user_id = users[users['Username'] == st.session_state['username']].iloc[0]['ID']
        user_registrations = registrations[registrations['UserID'] == user_id]
        
        for _, reg in user_registrations.iterrows():
            event_info = events[events['EventID'] == reg['EventID']].iloc[0]
            with st.expander(f"{event_info['Event Name']} on {event_info['Date']}"):
                st.write(f"**Date:** {event_info['Date']}")
                st.write(f"**Time:** {event_info['Time']}")
                st.write(f"**Day:** {event_info['Day']}")
                st.write(f"**Status:** {reg['Status']}")

    # Contact Us tab
    with tabs[2]:
        st.subheader("Contact Us")
        with st.form(key='contact_us_form'):
            message = st.text_area("Your Message", key="contact_message")
            submit_button = st.form_submit_button(label='Send Message')

        if submit_button:
            if message:
                users = load_data(USER_DATA_FILE)
                user_id = users[users['Username'] == st.session_state['username']].iloc[0]['ID']
                messages = load_data(MESSAGES_DATA_FILE)
                new_message = {
                    'UserID': user_id,
                    'Message': message,
                    'Response': ''
                }
                save_data(MESSAGES_DATA_FILE, pd.concat([messages, pd.DataFrame([new_message])], ignore_index=True))
                st.success("Message sent successfully!")
            else:
                st.error("Please write a message.")
        
        st.subheader("Admin Responses")
        messages = load_data(MESSAGES_DATA_FILE)
        users = load_data(USER_DATA_FILE)
        user_id = users[users['Username'] == st.session_state['username']].iloc[0]['ID']
        user_messages = messages[messages['UserID'] == user_id]

        for _, message in user_messages.iterrows():
            st.write(f"**Your Message:** {message['Message']}")
            st.write(f"**Admin Response:** {message['Response']}")

    # File Exchange tab
    # File Exchange tab (continued)
    # File Exchange tab (User Panel)
    # File Exchange tab (User Panel)
    # File Exchange tab (User Panel)
    # File Exchange tab (User Panel)
    # File Exchange tab (User Panel)
    # File Exchange tab (User Panel)
    with tabs[3]:
        st.subheader("File Exchange")
        
        st.write("**Files from Admin**")
        files = load_data(FILES_DATA_FILE)
        users = load_data(USER_DATA_FILE)
        user_id = users[users['Username'] == st.session_state['username']].iloc[0]['ID']
        
        admin_files = files[(files['UserID'] == user_id) & (files['FromAdmin'] == 'True')]
        for index, file in admin_files.iterrows():
            st.write(f"**Filename:** {file['Filename']}")
            st.download_button(
                "Download", 
                data=BytesIO(bytes(eval(file['FileData']))), 
                file_name=file['Filename'],
                key=f"download_admin_{index}"  # Unique key for each button
            )
        
        st.write("**Upload File for Admin**")
        uploaded_file = st.file_uploader("Choose a file")
        if uploaded_file is not None:
            if st.button("Upload and Send to Admin"):
                file_data = uploaded_file.getvalue()
                new_file = {
                    'UserID': user_id,
                    'Filename': uploaded_file.name,
                    'FileData': str(list(file_data)),  # Convert bytes to list of integers and store as string
                    'FromAdmin': 'False'
                }
                files = pd.concat([files, pd.DataFrame([new_file])], ignore_index=True)
                save_data(FILES_DATA_FILE, files)
                st.success("File sent successfully!")





# Main function to control navigation
def main():
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
    elif st.session_state['logged_in']:
        if st.session_state['is_admin']:
            admin_panel()
        else:
            user_panel()
    else:
        login()

if __name__ == '__main__':
    main()
            # File Exchange tab (continued)
    
