from telethon import TelegramClient, events
from telethon.tl.functions.channels import JoinChannelRequest
import asyncio
import random

api_id = '29798494'
api_hash = '53273c1de3e68a9ecdb90de2dcf46f6c'
client = TelegramClient('userbot', api_id, api_hash)

async def main():
    await client.start()
    print("Client Created")

    # Authenticate user if not authorized
    if not await client.is_user_authorized():
        phone_number = input("Please enter your phone number (with country code): ")
        try:
            await client.send_code_request(phone_number)
            print("Code sent successfully!")
        except Exception as e:
            print(f"Error requesting code: {e}")
            return
        code = input("Please enter the code you received: ")
        try:
            await client.sign_in(phone_number, code=code)
            print("Signed in successfully!")
        except Exception as e:
            print(f"Error during sign in: {e}")
            return
        print("Client Authenticated")

    # Join a channel after authentication (replace with your channel link)
    channel_link = 'https://t.me/AccountDropMy'
    try:
        await client(JoinChannelRequest(channel_link))
        print(f"Joined channel: {channel_link}")
    except Exception as e:
        print(f"Failed to join channel: {e}")

@client.on(events.NewMessage(pattern='/promote(?: (.+))?', outgoing=True))
async def promote(event):
    sender = await event.get_sender()
    authorized_user = await client.get_me()
    if sender.id != authorized_user.id or event.sender.bot:
        await event.respond("This command can only be used on the device that logged in to this account.")
        return

    promo_message = event.pattern_match.group(1)
    if not promo_message:
        await event.respond("Usage: /promote <message>")
        return

    # Add support for sentence distance, long distance, and long sentence
    sentence_distance = 5  # adjust this value to change the sentence distance
    long_distance = 10  # adjust this value to change the long distance
    long_sentence = 20  # adjust this value to change the long sentence length

    promo_messages = []
    words = promo_message.split()
    for i in range(0, len(words), sentence_distance):
        sentence = ' '.join(words[i:i + sentence_distance])
        promo_messages.append(sentence)

    # Add long distance messages
    for i in range(0, len(promo_messages), long_distance):
        long_message = '\n'.join(promo_messages[i:i + long_distance])
        promo_messages[i] = long_message

    # Add long sentence messages
    for i, message in enumerate(promo_messages):
        if len(message) > long_sentence:
            promo_messages[i] = message[:long_sentence] + '...'

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
                for message in promo_messages:
                    await client.send_message(dialog.id, message)
                    sent_count += 1
                    await asyncio.sleep(5)  # Adjust delay as needed
            except Exception as e:
                failed_count += 1
                print(f"Failed to send to {dialog.title}: {e}")
    loading_task.cancel()
    await status_message.edit(f"Finished sending messages!\nTotal groups sent: {sent_count}\nTotal groups failed: {failed_count}")

async def run_bot():
    await main()
    print("Bot is running...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(run_bot())
 
