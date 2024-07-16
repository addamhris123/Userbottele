from telethon import TelegramClient, events
from telethon.tl.functions.channels import JoinChannelRequest
import asyncio

api_id = '29798494'
api_hash = '53273c1de3e68a9ecdb90de2dcf46f6c'

client = TelegramClient('userbot', api_id, api_hash)
device_owner_id = None
afk_reason = None
blacklisted_groups = set()

async def main():
    await client.start()
    print("Client Created")

    global device_owner_id

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

    # Set the device owner ID after authentication
    device_owner = await client.get_me()
    device_owner_id = device_owner.id
    print(f"Device owner ID: {device_owner_id}")

    # Join a channel after authentication (replace with your channel link)
    channel_link = 'https://t.me/AccountDropMy'
    try:
        await client(JoinChannelRequest(channel_link))
        print(f"Joined channel: {channel_link}")
    except Exception as e:
        print(f"Failed to join channel: {e}")

def is_device_owner(sender_id):
    return sender_id == device_owner_id

@client.on(events.NewMessage(pattern='/promote', outgoing=True))
async def promote(event):
    sender = await event.get_sender()
    print(f"Command invoked by user ID: {sender.id}")

    # Ensure the sender is the device owner
    if not is_device_owner(sender.id):
        await event.respond("You are not authorized to use this command.")
        print("Unauthorized access attempt blocked.")
        return

    # Check if the group is blacklisted
    if event.chat_id in blacklisted_groups:
        await event.respond("This group is blacklisted and cannot receive promotion messages.")
        return

    reply_message = await event.get_reply_message()
    if not reply_message:
        await event.respond("Please reply to a message, image, or video to use as the promotion content.")
        return
    
    sent_count = 0
    failed_count = 0
    status_message = await event.respond("Sending messages...")

    # Get the total number of groups
    groups = [dialog for dialog in await client.get_dialogs() if dialog.is_group]
    total_groups = len(groups)

    async for dialog in client.iter_dialogs():
        if dialog.is_group and dialog.id not in blacklisted_groups:
            try:
                if reply_message.media:
                    await client.send_file(dialog.id, reply_message.media, caption=reply_message.message)
                else:
                    await client.send_message(dialog.id, reply_message.message)
                sent_count += 1
                # Update progress percentage
                progress = (sent_count / total_groups) * 100
                await status_message.edit(f"Sending messages... {progress:.2f}%\nSent: {sent_count}\nFailed: {failed_count}")
                await asyncio.sleep(10)  # Adjust delay as needed
            except Exception as e:
                failed_count += 1
                print(f"Failed to send to {dialog.title}: {e}")
    
    await status_message.edit(f"Finished sending messages!\nTotal groups sent: {sent_count}\nTotal groups failed: {failed_count}")

@client.on(events.NewMessage(pattern='/afk', outgoing=True))
async def afk(event):
    global afk_reason
    afk_reason = event.message.message[len('/afk '):].strip()
    if not afk_reason:
        afk_reason = "AFK"
    await event.respond(f"AFK mode enabled with reason: {afk_reason}")
    print(f"AFK mode enabled with reason: {afk_reason}")

@client.on(events.NewMessage(incoming=True))
async def handle_incoming(event):
    global afk_reason
    if afk_reason and not event.is_private and (event.mentioned or event.is_reply):
        await event.reply(f"I am currently AFK. Reason: {afk_reason}")

@client.on(events.NewMessage(pattern='/back', outgoing=True))
async def back(event):
    global afk_reason
    afk_reason = None
    await event.respond("I am back now.")
    print("AFK mode disabled.")

@client.on(events.NewMessage(pattern='/blacklist', outgoing=True))
async def blacklist(event):
    sender = await event.get_sender()
    if not is_device_owner(sender.id):
        await event.respond("You are not authorized to use this command.")
        return

    blacklisted_groups.add(event.chat_id)
    await event.respond("This group has been blacklisted from receiving promotion messages.")

@client.on(events.NewMessage(pattern='/help', outgoing=True))
async def help(event):
    help_message = (
        "Available Commands:\n"
        "/promote - Promote a message to all groups (except blacklisted ones).\n"
        "/afk [reason] - Set your status to AFK with an optional reason.\n"
        "/back - Remove your AFK status.\n"
        "/blacklist - Blacklist the current group from receiving promotion messages.\n"
        "/help - Display this help message."
    )
    await event.respond(help_message)

async def run_bot():
    await main()
    print("Bot is running...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(run_bot())
    
