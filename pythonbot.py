import telebot
import schedule
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from threading import Thread

# Initialize the bot with your API key
bot = telebot.TeleBot('put-your-api-key', parse_mode=None)

# Store checklist items in memory
checklist = [
    {"item": "Read or listen to Brahmaswarup Pramukh Swami Maharaj’s Jivan Charitra (Gujarati)", "completed": False},
    {"item": "Read Prasangam of Pramukh Swami Maharaj and Mahant Swami Maharaj (English)", "completed": False},
    {"item": "Join and read prasangs from the “Moments with Mahant Swami” Telegram Group tiny.cc/momentswithMahantSwami", "completed": False},
    {"item": "One month of Ektana, Dharna Parna, chandrayan or other vrats of their choice during Shavan Mas or for the duration of Chaturmas", "completed": False},
    {"item": "Listen to a 5-min Prapti no Vichar audio to begin developing the habit of doing it day", "completed": False},
    {"item": "Listen to or watch 7-10 minutes of Pramukh Swami Maharaj and Mahant Swami Maharaj’s prasangs/ashirvads daily", "completed": False},
    {"item": "Perform 2 extra malas a day", "completed": False},
    {"item": "Do extra dandvats and pradakshina during the four months of Chaturmas", "completed": False},
    {"item": "Regularly perform all ahnik (Puja, 2 Artis a day, Thal, Chesta) in one’s ghar mandir", "completed": False}
]

# Dictionary to store user-specific checklists
user_checklists = {}

# Command to send the checklist
@bot.message_handler(commands=["start", "checklist"])
def send_checklist(msg):
    user_id = msg.chat.id
    if user_id not in user_checklists:
        user_checklists[user_id] = checklist.copy()  # Create a copy of the checklist for the user
    markup = create_checklist_markup(user_checklists[user_id])
    bot.send_message(user_id, "Jai Swaminarayan, since Chaturmas is starting we would like you to take a few niyams. In order to run the bot, you'll have to fill in the boxes to which niyams you want to take. You will be getting daily reminders for the niyams you have chosen.:\nClick to toggle", reply_markup=markup)

# Function to create the checklist inline keyboard
def create_checklist_markup(user_checklist):
    markup = InlineKeyboardMarkup(row_width=1)
    for index, item in enumerate(user_checklist):
        if item["completed"]:
            button_text = f"✅ {item['item']}"
            callback_data = f"uncheck_{index}"
        else:
            button_text = f"❌ {item['item']}"
            callback_data = f"check_{index}"
        markup.add(InlineKeyboardButton(button_text, callback_data=callback_data))
    # Add a "Next" button at the end
    markup.add(InlineKeyboardButton("Next", callback_data="next"))
    return markup

# Callback query handler to toggle the state of checklist items
@bot.callback_query_handler(func=lambda call: call.data.startswith(('check_', 'uncheck_', 'next')))
def handle_query(call):
    user_id = call.message.chat.id
    if call.data == "next":
        bot.send_message(user_id, "Thank you! You will receive daily reminders for the niyams you have chosen.")
        return
    index = int(call.data.split('_')[1])
    user_checklist = user_checklists[user_id]
    user_checklist[index]["completed"] = not user_checklist[index]["completed"]
    markup = create_checklist_markup(user_checklist)
    bot.edit_message_reply_markup(user_id, call.message.message_id, reply_markup=markup)
    bot.answer_callback_query(call.id)

# Function to send daily reminders
def send_daily_reminders():
    for user_id, user_checklist in user_checklists.items():
        chosen_niyams = [item["item"] for item in user_checklist if item["completed"]]
        if chosen_niyams:
            reminder_message = "Daily Reminder:\n" + "\n".join(f"✅ {niyam}" for niyam in chosen_niyams)
            bot.send_message(user_id, reminder_message)

# Schedule daily reminders at a specific time (e.g., 7:00 AM)
schedule.every().day.at("19:00").do(send_daily_reminders)

# Function to run the schedule in a separate thread
def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Start the scheduler thread
thread = Thread(target=run_schedule)
thread.start()

# Start polling
bot.polling()
