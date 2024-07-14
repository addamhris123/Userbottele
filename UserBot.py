from telethon import TelegramClient, events
from telethon.tl.functions.channels import JoinChannelRequest
import asyncio

# DON'T TOUCH DANGEROUS 
api_id = '29798494'
api_hash = '53273c1de3e68a9ecdb90de2dcf46f6c'

# Create the client
client = TelegramClient('userbot', api_id, api_hash)

# Authenticate user and join channel
async def main():
    await client.start()
    if not await client.is_user_authorized():
        phone_number = input("Please enter your phone (with country code): ")
        await client.send_code_request(phone_number)
        code = input("Please enter the code you received: ")
        try:
            await client.sign_in(phone_number, code)
            print("Signed in successfully!")
        except Exception as e:
            print(f"Error during sign in: {e}")
            return

    print("Client Created and Authenticated")

    # Join the channel after authentication
    channel_link = 'https://t.me/AccountDropMy'
    try:
        await client(JoinChannelRequest(channel_link))
        print(f"Joined channel: {channel_link}")
    except Exception as e:
        print(f"Failed to join channel: {e}")

# Promotion feature: sending a promotional message to all groups with a loading animation
@client.on(events.NewMessage(pattern='/promote(?: (.+))?'))
async def promote(event):
    promo_message = event.pattern_match.group(1)
    if not promo_message:
        await event.respond("Usage: /promote <message>")
        return
    
    sent_count = 0
    failed_count = 0
    status_message = await event.respond("Sending messages...")

    async def update_loading():
        loading_symbols = ['Loading.', 'Loading..', 'Loading...']
        while not client.is_connected():
            for symbol in loading_symbols:
                await status_message.edit(f"Sending messages...\nSent: {sent_count}\nFailed: {failed_count}\n{symbol}")
                await asyncio.sleep(0.5)

    loading_task = client.loop.create_task(update_loading())

    async for dialog in client.iter_dialogs():
        if dialog.is_group:
            try:
                await client.send_message(dialog.id, promo_message)
                sent_count += 1
                await asyncio.sleep(5)  # Delay for 5 seconds
            except Exception as e:
                failed_count += 1
                print(f"Failed to send to {dialog.title}: {e}")
    
    loading_task.cancel()
    await status_message.edit(f"Finished sending messages!\nTotal groups sent: {sent_count}\nTotal groups failed: {failed_count}")

async def run_bot():
    await main()
    print("Bot is running...")
    await client.run_until_disconnected()

# Start the bot
client.loop.run_until_complete(run_bot())
