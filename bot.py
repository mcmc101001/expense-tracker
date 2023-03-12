import logging

from telegram.ext import(
    Application,
    ContextTypes,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters
)

from telegram.constants import ChatAction
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

from asgiref.sync import sync_to_async

import asyncio

import re

from functools import wraps

# Import models from django
import os
os.environ["DJANGO_SETTINGS_MODULE"] = "expense_tracker.settings"
import django
django.setup()

from main.models import CustomUser, Expense
from django.contrib.auth.models import User

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define bot token
TOKEN = os.environ["BOT_TOKEN"]

# Define stages to conversation handler
PASSWORD, BUDGET, CRAZY = range(3)
EDIT_MODE, EDIT_VALUE = range(2)
NAME_EXPENSE, COST_EXPENSE, TYPE_EXPENSE = range(3)

# Define constants
type_list = ["Meals", "Snacks", "Gifts", "Clothes", "Transport", "Entertainment", "Won't use but still buy", "Misc."]
edit_profile_list = ["Password", "Budget", "Crazy mode"]
boolean_list = ["Yes", "No"]

# Define typing decorator function
def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        async def command_func(update, context, *args, **kwargs):
            if update.message == None:
                return
            await context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return await func(update, context,  *args, **kwargs)
        return command_func
    
    return decorator

# Define command handlers
def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

@send_action(ChatAction.TYPING) 
async def help(update, context):
    """Send a message when the command /help is issued."""
    text_file = open("help.txt", encoding="utf8" , mode="r")
    data = text_file.read()
    text_file.close()
    await update.message.reply_text(data)

# Define cancel command to end conversations
@send_action(ChatAction.TYPING)     
async def cancel(update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Operation cancelled succesfully!", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

@send_action(ChatAction.TYPING) 
async def support(update, context):
    """Send a message when the command /support is issued."""
    await update.message.reply_photo(open("paylahqr.jfif", "rb"))
    await update.message.reply_text('Thanks for the support! Much appreciated 🫶')

@send_action(ChatAction.TYPING) 
async def track(update, context):
    """Send a message when the command /track is issued."""
    url = "https://expensetrackertelegram.up.railway.app/main/expense_list"
    await update.message.reply_text("URL to expense tracker site: "+url)

# Define django models async function
@sync_to_async
def create_user_async(username, password):
    User.objects.create_user(username=username, password=password)

@sync_to_async
def set_password_async(username, password):
    current_user = User.objects.get(username=username)
    current_user.set_password(password)
    current_user.save()    
    

# Define start function, profile creation
@send_action(ChatAction.TYPING) 
async def start(update, context):
    """Send a message when the command /start is issued. Asks for password if profile not created."""
    await update.message.reply_text('Hi! I assist in helping you track expenses! Use /help to understand more about the bot!')
    username = update.message.from_user.username
    if await User.objects.filter(username=username).aexists():
        await update.message.reply_text('It seems that your user profile has already been created! Use /editprofile to change your details.')
        return ConversationHandler.END
    await update.message.reply_text('Hi, please enter the password for your account. Make sure that you use at least 8 characters which are not entirely numeric. Please do not use emojis or anything :(')
    return PASSWORD

@send_action(ChatAction.TYPING) 
async def password(update, context):
    """Asks for budget"""
    if update.message.text.isnumeric():
        await update.message.reply_text("HEY LISTEN TO INSTRUCTIONS MAN!")
        return PASSWORD
    if (len(update.message.text) < 8):
        await update.message.reply_text("HEY LISTEN TO INSTRUCTIONS MAN!")
        return PASSWORD
    await create_user_async(username=update.message.from_user.username, password=update.message.text)
    await update.message.reply_text("Please input a monthly budget (only integers) to receive a warning if exceeded. Input 0 if no budget is needed.")
    return BUDGET
    
@send_action(ChatAction.TYPING) 
async def budget(update, context):
    """Ask if want crazy mode"""
    if not update.message.text.isnumeric():
        await update.message.reply_text("HEY LISTEN TO INSTRUCTIONS MAN!")
        return BUDGET
    if len(update.message.text) > 8:
        await update.message.reply_text("Please use a lower budget.")
        return BUDGET
    context.user_data["budget"] = int(update.message.text)
    reply_keyboard = [["Yes", "No"]]
    await update.message.reply_text(
        "Please select if you want crazy mode enabled (flame you everytime you make an expense).",
        reply_markup = ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Crazy mode"
        ),
    )
    return CRAZY
    
@send_action(ChatAction.TYPING) 
async def crazy(update, context):
    """Saves user"""
    if update.message.text not in boolean_list:
        await update.message.reply_text("Please use the reply keyboard.")
        return CRAZY
    if update.message.text == "Yes":
        crazy_mode = True
    else:
        crazy_mode = False
    current_user = await User.objects.aget(username=update.message.from_user.username)
    budget_user = context.user_data["budget"]
    await CustomUser.objects.acreate(user=current_user, budget=budget_user, constant_reminder=crazy_mode)
    await update.message.reply_text(
        "Profile created successfully! Your username is your telegram username. You can use /help to discover functions of the bot!", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

# Define edit profile function
@send_action(ChatAction.TYPING) 
async def editProfile(update, context):
    """Allows user to edit profile."""
    # check if profile created, then edit
    if not await User.objects.filter(username=update.message.from_user.username).aexists():
        await update.message.reply_text('It seems that your user profile has not been created! Use /start to create your profile.')
        return ConversationHandler.END
    reply_keyboard = [["Password"], ["Budget", "Crazy mode"]]
    await update.message.reply_text(
        "Please select the type of profile edit.",
        reply_markup = ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Edit profile"
        ),
    )
    return EDIT_MODE

@send_action(ChatAction.TYPING) 
async def editMode(update, context):
    if update.message.text not in edit_profile_list:
        await update.message.reply_text("PLEASE USE THE REPLY KEYBOARD OMG STOP TESTING ME")
        return EDIT_MODE
    if update.message.text == "Password":
        context.user_data["edit_mode"] = "Password"
        await update.message.reply_text(
            'Hi, please enter the password for your account. Make sure that you use at least 8 characters which are not entirely numeric. Please do not use emojis or anything :(', reply_markup = ReplyKeyboardRemove()
        )
    if update.message.text == "Budget":
        context.user_data["edit_mode"] = "Budget"
        await update.message.reply_text(
            "Please input a monthly budget (only integers) to receive a warning if exceeded. Input 0 if no budget is needed.", reply_markup = ReplyKeyboardRemove()
        )
    if update.message.text == "Crazy mode":
        context.user_data["edit_mode"] = "Crazy mode"
        reply_keyboard = [["Yes", "No"]]
        await update.message.reply_text(
        "Please select if you want crazy mode enabled (flame you everytime you make an expense).",
        reply_markup = ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Crazy mode"
        ),
    )
    return EDIT_VALUE

@send_action(ChatAction.TYPING) 
async def editValue(update, context):
    if context.user_data["edit_mode"] == "Password":
        if update.message.text.isnumeric():
            await update.message.reply_text("HEY LISTEN TO INSTRUCTIONS MAN!")
            return EDIT_VALUE
        if len(update.message.text) < 8:
            await update.message.reply_text("HEY LISTEN TO INSTRUCTIONS MAN!")
            return EDIT_VALUE
        await set_password_async(username=update.message.from_user.username, password=update.message.text)
    if context.user_data["edit_mode"] == "Budget":
        if not update.message.text.isnumeric():
            await update.message.reply_text("HEY LISTEN TO INSTRUCTIONS MAN!")
            return EDIT_VALUE
        if len(update.message.text) > 8:
            await update.message.reply_text("Please use a lower budget.")
            return EDIT_VALUE
        current_user = await User.objects.aget(username=update.message.from_user.username)
        await CustomUser.objects.filter(user=current_user).aupdate(budget=int(update.message.text))
    if context.user_data["edit_mode"] == "Crazy mode":
        if update.message.text not in boolean_list:
            await update.message.reply_text("Please use the reply keyboard.")
            return EDIT_VALUE
        if update.message.text == "Yes":
            crazy_mode = True
        else:
            crazy_mode = False
        current_user = await User.objects.aget(username=update.message.from_user.username)
        await CustomUser.objects.filter(user=current_user).aupdate(constant_reminder=crazy_mode)
    await update.message.reply_text(
            "Profile saved successfully!", reply_markup = ReplyKeyboardRemove()
        )
    return ConversationHandler.END

# Define add expense function
@send_action(ChatAction.TYPING)
async def expense(update, context):
    """Asks for name of expense"""
    await update.message.reply_text("Please type the name of your expense!")
    return NAME_EXPENSE

@send_action(ChatAction.TYPING)
async def name_expense(update, context):
    """Asks for cost of expense"""
    if(len(update.message.text)>250):
        await update.message.reply_text("Please use a shorter name!")
        return NAME_EXPENSE
    context.user_data["name_expense"] = update.message.text
    await update.message.reply_text("Please type the cost of your expense!")
    return COST_EXPENSE

@send_action(ChatAction.TYPING)
async def cost_expense(update, context):
    """Asks for type of expense"""
    regex = "^\d+(\.)?(\d{0,2}$)"
    if re.match(regex, update.message.text) == None:
        await update.message.reply_text("Please use only numbers with max 2 decimal places!")
        return COST_EXPENSE
    try:
        context.user_data["cost_expense"] = float(update.message.text)
    except ValueError:
        await update.message.reply_text("Error 101! Please contact admin.")
        return ConversationHandler.END
    reply_keyboard = [["Meals","Snacks"],["Gifts", "Clothes"],["Transport", "Entertainment"],["Won't use but still buy", "Misc."]]
    await update.message.reply_text(
        "Please select the type of expense.",
        reply_markup = ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Expense type"
        ),
    )
    return TYPE_EXPENSE

@send_action(ChatAction.TYPING)
async def type_expense(update, context):
    """Saves expense to database"""
    if update.message.text not in type_list:
        await update.message.reply_text("Please use the reply keyboard")
        return TYPE_EXPENSE
    type_expense = update.message.text
    cost_expense = context.user_data["cost_expense"]
    name_expense = context.user_data["name_expense"]
    current_user = await User.objects.aget(username=update.message.from_user.username)
    user_expense = await CustomUser.objects.aget(user=current_user)
    await Expense.objects.acreate(name=name_expense, type=type_expense, cost=cost_expense, user=user_expense)
    if user_expense.constant_reminder == True:
        await update.message.reply_text(
            "Expense successfully saved! \n\nBUT IT SHOULD'T BE COS YOU ARE SPENDING FAR TOO MUCH. YOU THINK MONEY GROW ON TREES ISSIT. STOP SPENDING MONEY AND SAVE SOME OF THAT FOR YOUR FUTURE. OH WAIT AT THIS RATE YOUR FUTURE IS GONNA BE NON-EXISTENT ANYWAYS. YOU DO YOU THEN.", reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    await update.message.reply_text(
        "Expense successfully saved!", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

# Define main function
def main():
    """ Start the bot """
    app = Application.builder().token(TOKEN).build()
    
    user_creation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states = {
            PASSWORD: [MessageHandler(filters.TEXT & (~ filters.COMMAND), password)],
            BUDGET: [MessageHandler(filters.TEXT & (~ filters.COMMAND), budget)],
            CRAZY: [MessageHandler(filters.TEXT & (~ filters.COMMAND), crazy)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    edit_handler = ConversationHandler(
        entry_points=[CommandHandler("editprofile", editProfile)],
        states={
            EDIT_MODE: [MessageHandler(filters.TEXT & (~ filters.COMMAND), editMode)],
            EDIT_VALUE: [MessageHandler(filters.TEXT & (~ filters.COMMAND), editValue)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    expense_handler = ConversationHandler(
        entry_points=[CommandHandler("expense", expense)],
        states={
            NAME_EXPENSE: [MessageHandler(filters.TEXT & (~ filters.COMMAND), name_expense)],
            COST_EXPENSE: [MessageHandler(filters.TEXT & (~ filters.COMMAND), cost_expense)],
            TYPE_EXPENSE: [MessageHandler(filters.TEXT & (~ filters.COMMAND), type_expense)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    """ Add command handlers """
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("track", track))
    app.add_handler(CommandHandler("support", support))
    app.add_handler(user_creation_handler)
    app.add_handler(edit_handler)
    app.add_handler(expense_handler)
    
    """ Log all errors """
    app.add_error_handler(error)
    
    """ Start the bot """
    app.run_polling()
    
if __name__ == '__main__':
    main()