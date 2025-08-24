import asyncio
from telegram import Bot
from telegram.error import TelegramError

class TelegramNotifier:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.bot = Bot(token=self.bot_token)
    
    async def send_notification(self, message):
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            return True
        except TelegramError as e:
            print(f"Error sending message: {e}")
            return False
    
    async def send_notification_with_formatting(self, title, content):
        formatted_message = f"<b>{title}</b>\n\n{content}"
        return await self.send_notification(formatted_message)

# Usage example
async def main():
    # Replace with your actual bot token and chat ID
    BOT_TOKEN = ""
    CHAT_ID = ""
    
    notifier = TelegramNotifier(BOT_TOKEN, CHAT_ID)
    
    # Send a simple notification
    await notifier.send_notification("This is a test notification!")
    
    # Send a formatted notification
    await notifier.send_notification_with_formatting(
        title="System Alert",
        content="Your scheduled task has completed successfully."
    )

if __name__ == "__main__":
    asyncio.run(main())
