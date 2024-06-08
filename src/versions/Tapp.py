import pandas as pd
from datetime import datetime
import os
from io import BytesIO
from telegram import Update, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, CallbackContext, 
    ConversationHandler, CallbackQueryHandler
)
from telegram.ext.filters import TEXT, COMMAND


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
            df = pd.DataFrame(columns=['UserID', 'Message', 'Response'])
        elif file == FILES_DATA_FILE:
            df = pd.DataFrame(columns=['UserID', 'Filename', 'FileData', 'FromAdmin'])
        elif file == CONTACT_DATA_FILE:
            df = pd.DataFrame(columns=['UserID', 'Subject', 'Message'])
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

# States for ConversationHandler
LOGIN, REGISTER, MAIN_MENU, ADMIN_PANEL, USER_PANEL, CONTACT_ADMIN, FILE_EXCHANGE = range(7)

def start(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    context.user_data['telegram_id'] = user.id
    update.message.reply_text(
        'Welcome! Please choose an option:',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Login", callback_data='login')],
            [InlineKeyboardButton("Sign Up", callback_data='sign_up')]
        ])
    )
    return LOGIN

def login(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Please enter your username:")
    return LOGIN

def handle_login_username(update: Update, context: CallbackContext) -> int:
    context.user_data['username'] = update.message.text
    update.message.reply_text("Please enter your password:")
    return LOGIN

def handle_login_password(update: Update, context: CallbackContext) -> int:
    password = update.message.text
    username = context.user_data['username']
    
    if check_credentials(username, password):
        context.user_data['logged_in'] = True
        context.user_data['username'] = username
        if username == 'admin':
            context.user_data['is_admin'] = True
            return admin_panel(update, context)
        else:
            context.user_data['is_admin'] = False
            return user_panel(update, context)
    else:
        update.message.reply_text("Invalid credentials. Please try again.")
        return LOGIN

def sign_up(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Please enter your name:")
    return REGISTER

def handle_sign_up(update: Update, context: CallbackContext) -> int:
    context.user_data['name'] = update.message.text
    update.message.reply_text("Please enter your last name:")
    return REGISTER

def handle_sign_up_last_name(update: Update, context: CallbackContext) -> int:
    context.user_data['last_name'] = update.message.text
    update.message.reply_text("Please enter your mobile number:")
    return REGISTER

def handle_sign_up_mobile(update: Update, context: CallbackContext) -> int:
    context.user_data['mobile_number'] = update.message.text
    update.message.reply_text("Please enter your Telegram ID:")
    return REGISTER

def handle_sign_up_telegram(update: Update, context: CallbackContext) -> int:
    context.user_data['telegram_id'] = update.message.text
    update.message.reply_text("Please choose a username:")
    return REGISTER

def handle_sign_up_username(update: Update, context: CallbackContext) -> int:
    username = update.message.text
    if username_exists(username):
        update.message.reply_text("Username already exists. Please choose a different username.")
        return REGISTER
    context.user_data['username'] = username
    update.message.reply_text("Please choose a password:")
    return REGISTER

def handle_sign_up_password(update: Update, context: CallbackContext) -> int:
    password = update.message.text
    context.user_data['password'] = password
    
    # Save the user
    users = load_data(USER_DATA_FILE)
    user_id = len(users) + 1
    user_data = {
        'ID': str(user_id),
        'Name': context.user_data['name'],
        'Last Name': context.user_data['last_name'],
        'Mobile Number': context.user_data['mobile_number'],
        'Telegram ID': context.user_data['telegram_id'],
        'Username': context.user_data['username'],
        'Password': context.user_data['password']
    }
    save_data(USER_DATA_FILE, pd.concat([users, pd.DataFrame([user_data])], ignore_index=True))
    update.message.reply_text("User registered successfully! You can now log in.")
    
    return start(update, context)

def admin_panel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'Admin Panel:\n1. Create Event\n2. View Registered Users\n3. Remove Event\n4. View All Users\n5. User Messages\n6. File Exchange\n\nPlease choose an option by sending the number.',
    )
    return ADMIN_PANEL

def user_panel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'User Panel:\n1. View Events\n2. My Registrations\n3. Contact Admin\n4. File Exchange\n\nPlease choose an option by sending the number.',
    )
    return USER_PANEL

def main_menu(update: Update, context: CallbackContext) -> int:
    if context.user_data['is_admin']:
        return admin_panel(update, context)
    else:
        return user_panel(update, context)

def contact_admin(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Please enter the subject of your message:")
    return CONTACT_ADMIN

def handle_contact_subject(update: Update, context: CallbackContext) -> int:
    context.user_data['subject'] = update.message.text
    update.message.reply_text("Please enter your message:")
    return CONTACT_ADMIN

def handle_contact_message(update: Update, context: CallbackContext) -> int:
    context.user_data['message'] = update.message.text
    
    # Save the message
    users = load_data(USER_DATA_FILE)
    user_id = users[users['Username'] == context.user_data['username']].iloc[0]['ID']
    
    new_message = {
        'UserID': user_id,
        'Subject': context.user_data['subject'],
        'Message': context.user_data['message']
    }
    messages = load_data(CONTACT_DATA_FILE)
    messages = pd.concat([messages, pd.DataFrame([new_message])], ignore_index=True)
    save_data(CONTACT_DATA_FILE, messages)
    update.message.reply_text("Message sent successfully!")
    
    return main_menu(update, context)

def file_exchange(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Please send the file you want to upload:")
    return FILE_EXCHANGE

def handle_file_upload(update: Update, context: CallbackContext) -> int:
    file = update.message.document
    user_id = context.user_data['telegram_id']
    file_data = context.bot.get_file(file.file_id).download_as_bytearray()
    new_file = {
        'UserID': user_id,
        'Filename': file.file_name,
        'FileData': file_data,
        'FromAdmin': context.user_data['is_admin']
    }
    files = load_data(FILES_DATA_FILE)
    files = pd.concat([files, pd.DataFrame([new_file])], ignore_index=True)
    save_data(FILES_DATA_FILE, files)
    update.message.reply_text("File uploaded successfully!")
    
    return main_menu(update, context)

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Cancelled. Use /start to begin again.')
    return ConversationHandler.END

def main():
    updater = Updater("7001134220:AAFcmjBBcgZQxQCge7OF3qbHFDswPcacr6U", use_context=True)

    dispatcher = updater.dispatcher
    
    # Define the conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            LOGIN: [
                CallbackQueryHandler(login, pattern='^login$'),
                CallbackQueryHandler(sign_up, pattern='^sign_up$'),
                MessageHandler(TEXT & ~COMMAND, handle_login_username),
                MessageHandler(TEXT & ~COMMAND, handle_login_password)
            ],
            REGISTER: [
                MessageHandler(TEXT & ~COMMAND, handle_sign_up),
                MessageHandler(TEXT & ~COMMAND, handle_sign_up_last_name),
                MessageHandler(TEXT & ~COMMAND, handle_sign_up_mobile),
                MessageHandler(TEXT & ~COMMAND, handle_sign_up_telegram),
                MessageHandler(TEXT & ~COMMAND, handle_sign_up_username),
                MessageHandler(TEXT & ~COMMAND, handle_sign_up_password)
            ],
            ADMIN_PANEL: [
                MessageHandler(TEXT & ~COMMAND, admin_panel)
            ],
            USER_PANEL: [
                MessageHandler(TEXT & ~COMMAND, user_panel)
            ],
            CONTACT_ADMIN: [
                MessageHandler(TEXT & ~COMMAND, handle_contact_subject),
                MessageHandler(TEXT & ~COMMAND, handle_contact_message)
            ],
          
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    dispatcher.add_handler(conv_handler)
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
