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
            registrations = registrations[registrations['EventID'] != event_id]
            save_data(EVENT_DATA_FILE, events)
            save_data(REGISTRATION_DATA_FILE, registrations)
            st.success("Event removed successfully! ❌")

    # View All Users tab
    with tabs[3]:
        st.subheader("All Users 👥")
        users = load_data(USER_DATA_FILE)
        st.write(users[['ID', 'Name', 'Last Name', 'Mobile Number', 'Telegram ID', 'Username']])

    # User Messages tab
    # User Messages tab
    with tabs[4]:
        st.subheader("User Messages ✉️")

        messages = load_data(CONTACT_DATA_FILE)  # Ensure messages are loaded from CONTACT_DATA_FILE
        users = load_data(USER_DATA_FILE)

        if not messages.empty:
            user_ids = messages['UserID'].unique()
            user_dict = {user_id: users[users['ID'] == user_id].iloc[0]['Username'] for user_id in user_ids}
            selected_user = st.selectbox("Select User", options=list(user_dict.keys()), format_func=lambda x: user_dict[x])

            user_messages = messages[messages['UserID'] == selected_user]
            for index, message in user_messages.iterrows():
                user_info = users[users['ID'] == selected_user].iloc[0]
                st.write(f"**From:** {user_info['Name']} {user_info['Last Name']} ({user_info['Username']})")
                st.write(f"**Subject:** {message['Subject']}")
                st.write(f"**Message:** {message['Message']}")
                response = st.text_area(f"Response to {user_info['Username']}:", key=f"response_{message['UserID']}_{index}")
                if st.button("Send Response", key=f"send_{message['UserID']}_{index}"):
                    if response:
                        # Update the DataFrame with the response
                        messages.at[index, 'Response'] = response
                        save_data(CONTACT_DATA_FILE, messages)  # Save back to CONTACT_DATA_FILE
                        st.success("Response sent successfully!")
                    else:
                        st.warning("Response cannot be empty.")
                st.write("---")
        else:
            st.write("No messages from users.")

    # File Exchange tab
    with tabs[5]:
        st.subheader("File Exchange")
        
        st.write("**Files from Users**")
        files = load_data(FILES_DATA_FILE)
        users = load_data(USER_DATA_FILE)
        
        user_files = files[files['FromAdmin'] == 'False']
        if not user_files.empty:
            user_ids = user_files['UserID'].unique()
            user_dict = {user_id: users[users['ID'] == user_id].iloc[0]['Username'] for user_id in user_ids}
            selected_user = st.selectbox("Select User", options=list(user_dict.keys()), format_func=lambda x: user_dict[x])
            
            user_files_selected = user_files[user_files['UserID'] == selected_user]
            for index, file in user_files_selected.iterrows():
                st.write(f"**Filename:** {file['Filename']}")
                st.download_button(
                    "Download", 
                    data=BytesIO(bytes(eval(file['FileData']))), 
                    file_name=file['Filename'],
                    key=f"download_user_{index}"  # Unique key for each button
                )
        else:
            st.write("No files from users.")
        
        st.write("**Upload File for Users**")
        uploaded_file = st.file_uploader("Choose a file")
        if uploaded_file is not None:
            user_options = users['Username'].tolist()
            user_to_send = st.selectbox("Select User to Send", user_options)
            if st.button("Upload and Send"):
                user_id_to_send = users[users['Username'] == user_to_send].iloc[0]['ID']
                file_data = uploaded_file.getvalue()
                new_file = {
                    'UserID': user_id_to_send,
                    'Filename': uploaded_file.name,
                    'FileData': str(list(file_data)),
                    'FromAdmin': 'True'
                }
                files = pd.concat([files, pd.DataFrame([new_file])], ignore_index=True)
                save_data(FILES_DATA_FILE, files)
                st.success("File sent successfully!")
    # User panel
def user_panel():
    
    st.title("User Panel 🎨")

    tabs = st.tabs(["View Events 📅", "My Registrations 🗂️", "Messages ✉️", "Contact Admin 📧", "File Exchange 📂"])

    # View Events tab
    with tabs[0]:
        st.subheader("Events 📅")
        events = load_data(EVENT_DATA_FILE)
        registrations = load_data(REGISTRATION_DATA_FILE)
        users = load_data(USER_DATA_FILE)
        user_id = users[users['Username'] == st.session_state['username']]['ID'].values[0]

        for _, event in events.iterrows():
            with st.expander(f"{event['Event Name']} on {event['Date']}"):
                st.write(f"**Time:** {event['Time']}")
                st.write(f"**Day:** {event['Day']}")
                st.write(f"**Max Volunteers:** {event['Max Volunteers']}")
                st.write(f"**Reserve Capacity:** {event['Reserve Capacity']}")

                registered_users = registrations[(registrations['EventID'] == str(event['EventID'])) & (registrations['Status'] == 'Registered')]
                reserve_users = registrations[(registrations['EventID'] == str(event['EventID'])) & (registrations['Status'] == 'Reserve')]

                if user_id in registered_users['UserID'].values:
                    st.write("You are registered for this event.")
                elif user_id in reserve_users['UserID'].values:
                    st.write("You are on the reserve list for this event.")
                else:
                    if len(registered_users) < event['Max Volunteers']:
                        if st.button(f"Register for {event['Event Name']}"):
                            registrations = pd.concat([registrations, pd.DataFrame([{'UserID': user_id, 'EventID': str(event['EventID']), 'Status': 'Registered'}])], ignore_index=True)
                            save_data(REGISTRATION_DATA_FILE, registrations)
                            st.success("Registered successfully!")
                            st.experimental_rerun()
                    elif len(reserve_users) < int(event['Reserve Capacity']):  # Ensure comparison is valid
                        if st.button(f"Join Reserve List for {event['Event Name']}"):
                            registrations = pd.concat([registrations, pd.DataFrame([{'UserID': user_id, 'EventID': str(event['EventID']), 'Status': 'Reserve'}])], ignore_index=True)
                            save_data(REGISTRATION_DATA_FILE, registrations)
                            st.success("Added to reserve list!")
                            st.experimental_rerun()
                    else:
                        st.write("Event is full.")

    # My Registrations tab
    with tabs[1]:
        st.subheader("My Registrations 🗂️")
        registrations = load_data(REGISTRATION_DATA_FILE)
        events = load_data(EVENT_DATA_FILE)
        users = load_data(USER_DATA_FILE)
        user_id = users[users['Username'] == st.session_state['username']].iloc[0]['ID']

        user_registrations = registrations[registrations['UserID'] == user_id]

        if not user_registrations.empty:
            for _, reg in user_registrations.iterrows():
                event_info = events[events['EventID'] == reg['EventID']]
                if not event_info.empty:
                    event_info = event_info.iloc[0]
                    with st.expander(f"{event_info['Event Name']} on {event_info['Date']}"):
                        st.write(f"**Event:** {event_info['Event Name']}")
                        st.write(f"**Date:** {event_info['Date']}")
                        st.write(f"**Time:** {event_info['Time']}")
                        st.write(f"**Day:** {event_info['Day']}")
                        st.write(f"**Status:** {reg['Status']}")

                        if st.button(f"Cancel Registration for {event_info['Event Name']}", key=f"cancel_{reg['EventID']}"):
                            # Remove registration
                            registrations = registrations.drop(reg.name)

                            # Move the first person from the reserve list to registered list if main list is full
                            event_registrations = registrations[registrations['EventID'] == reg['EventID']]
                            main_list_count = len(event_registrations[event_registrations['Status'] == 'Registered'])
                            reserve_list = event_registrations[event_registrations['Status'] == 'Reserve']

                            if main_list_count < event_info['Max Volunteers'] and not reserve_list.empty:
                                # Move the first person from reserve to main list
                                first_reserve = reserve_list.iloc[0]
                                registrations.loc[first_reserve.name, 'Status'] = 'Registered'
                                st.success("Registration canceled successfully. Replaced with first person from reserve list!")
                            else:
                                st.success("Registration canceled successfully.")

                            save_data(REGISTRATION_DATA_FILE, registrations)
                            st.experimental_rerun()
        else:
            st.write("You have no registrations.")



    # Messages tab
        # Messages tab
    with tabs[2]:
        st.subheader("Messages ✉️")
        messages = load_data(CONTACT_DATA_FILE)  # Ensure messages are loaded from CONTACT_DATA_FILE
        users = load_data(USER_DATA_FILE)
        user_id = users[users['Username'] == st.session_state['username']]['ID'].values[0]

        user_messages = messages[messages['UserID'] == user_id]

        if not user_messages.empty:
            for _, message in user_messages.iterrows():
                st.write(f"**Subject:** {message['Subject']}")
                st.write(f"**Message:** {message['Message']}")
                st.write(f"**Response:** {message['Response']}")  # Display the response
        else:
            st.write("No messages.")


    # Contact Admin tab
    # Contact Admin tab
    with tabs[3]:
        st.subheader("Contact Admin 📧")
        with st.form(key='contact_admin_form'):
            subject = st.text_input("Subject", key="contact_subject")
            message = st.text_area("Message", key="contact_message")

            submit_button = st.form_submit_button(label='Send Message')

        if submit_button:
            if subject and message:
                messages = load_data(CONTACT_DATA_FILE)  # Ensure messages are loaded from CONTACT_DATA_FILE
                user_id = users[users['Username'] == st.session_state['username']]['ID'].values[0]
                message_data = {
                    'UserID': user_id,
                    'Subject': subject,
                    'Message': message,
                    'Response': ''  # Initialize with empty response
                }
                save_data(CONTACT_DATA_FILE, pd.concat([messages, pd.DataFrame([message_data])], ignore_index=True))  # Save to CONTACT_DATA_FILE
                st.success("Message sent to admin!")
            else:
                st.error("Please fill out all fields.")
    # File Exchange tab
    with tabs[4]:
        st.subheader("File Exchange")
        
        st.write("**Files from Admin**")
        files = load_data(FILES_DATA_FILE)
        users = load_data(USER_DATA_FILE)
        user_id = users[users['Username'] == st.session_state['username']].iloc[0]['ID']
        
        admin_files = files[(files['UserID'] == user_id) & (files['FromAdmin'] == 'True')]
        if not admin_files.empty:
            filenames = admin_files['Filename'].tolist()
            selected_file = st.selectbox("Select File", filenames)
            file_selected = admin_files[admin_files['Filename'] == selected_file].iloc[0]
            st.download_button(
                "Download", 
                data=BytesIO(bytes(eval(file_selected['FileData']))), 
                file_name=file_selected['Filename'],
                key=f"download_admin_{file_selected.name}"  # Unique key for each button
            )
        else:
            st.write("No files from admin.")
        
        st.write("**Upload File for Admin**")
        uploaded_file = st.file_uploader("Choose a file")
        if uploaded_file is not None:
            if st.button("Upload and Send to Admin"):
                file_data = uploaded_file.getvalue()
                new_file = {
                    'UserID': user_id,
                    'Filename': uploaded_file.name,
                    'FileData': str(list(file_data)),
                    'FromAdmin': 'False'
                }
                files = pd.concat([files, pd.DataFrame([new_file])], ignore_index=True)
                save_data(FILES_DATA_FILE, files)
                st.success("File sent successfully!")


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
