import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
from openai import OpenAI
from collections import deque

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)
TOKEN = os.getenv('TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

OpenAI.api_key = OPENAI_API_KEY
message_history = deque(maxlen=10)
client = OpenAI()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_history.clear()
    user_name = update.effective_user.username or update.effective_user.first_name or "User"
    logger.info(f"{user_name} used /start command")
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hey! I'm your AI assistant. \n Use /role to set the role of the AI, \n /reset to clear the conversation history, \n /history to view the conversation history, \n /clear to clear the conversation history but keep the role setting.")

async def role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username or update.effective_user.first_name or "User"
    logger.info(f"{user_name} used /role command")
    context.user_data["setting_role"] = True 
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Please, write what role should AI refer to")

async def reset(update: Update, context:ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username or update.effective_user.first_name or "User"
    logger.info(f"{user_name} used /reset command")
    context.user_data["bot_role"] = ''  
    context.user_data["setting_role"] = False  
    await context.bot.send_message(update.effective_chat.id, text='Role reset completed')

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username or update.effective_user.first_name or "User"
    logger.info(f"{user_name} used /history command")

    if not message_history:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="No conversation history yet.")
        return
    
    history_text = "Conversation History:\n\n"
    for msg in message_history:
        role = msg["role"].capitalize()
        content = msg["content"]
        if len(content) > 100:
            content = content[:97] + "..."
        history_text += f"{role}: {content}\n\n"
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text=history_text)

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username or update.effective_user.first_name or "User"
    logger.info(f"{user_name} used /clear command")

    message_history.clear()
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="Conversation history cleared."
    )

async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text
    user_name = update.effective_user.username or update.effective_user.first_name or "User"
    
    logger.info(f"Message from {user_name}: {message_text}")

    if context.user_data.get("setting_role"):
        context.user_data["bot_role"] = message_text
        context.user_data["setting_role"] = False
        await update.message.reply_text(f"Role has been set: {message_text}")
        logger.info(f"Bot role set to: {message_text}")
    else:
        message_history.append({"role": "user", "content": message_text})
        messages = []
        system_content = "You are a helpful, concise assistant that provides accurate and direct answers. Check all instructions before responding."
        bot_role = context.user_data.get("bot_role", "")
        if bot_role:
            system_content += f" {bot_role}."
        messages.append({"role": "system", "content": system_content})
        for msg in message_history:
            messages.append(msg)
            
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-nano",  
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
                top_p=1.0
            )

            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens
            logger.info(f"Token usage - Prompt: {prompt_tokens}, Completion: {completion_tokens}, Total: {total_tokens}")

            answer = response.choices[0].message.content.strip()
            if len(answer) > 4000:
                answer = answer[:4000] + "..."
                
            message_history.append({"role": "assistant", "content": answer})
            
            if not answer:
                answer = "I don't have a response for that. Please try again."
            
           
            logger.info(f"Bot response: {answer}")
                
            await context.bot.send_message(chat_id=update.effective_chat.id, text=answer)
        except Exception as e:
            logging.error(f"Error generating or sending response: {e}")
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text="Sorry, I encountered an error processing your request. Please try again."
            )
        
if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('role', role))
    application.add_handler(CommandHandler('reset', reset))
    application.add_handler(CommandHandler('history', history))
    application.add_handler(CommandHandler('clear', clear))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message))
    
    logger.info("Bot started. Listening for messages...")
    
    try:
        application.run_polling()
    except Exception as e:
        logger.error(f"Error running bot: {e}")
    finally:
        logger.info("Bot stopped")
