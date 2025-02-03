import discord
from discord.ext import commands
import requests
import json
from dotenv import load_dotenv
import os
from datetime import datetime
import random
import asyncio
from discord.ext import tasks

load_dotenv()

API_ENDPOINT = 'https://discord.com/api/v9'
VIEW_CHANNEL_ID = int(os.environ.get('VIEW_CHANNEL_ID'))
VIEW_USER_IDS = list(map(int, os.environ.get('VIEW_USER_IDS').split(',')))
SEND_CHANNEL_IDS = list(map(int, os.environ.get('SEND_CHANNEL_IDS').split(',')))
AUTH_TOKEN = os.environ.get('AUTH_TOKEN')
BOT_TOKEN = os.environ.get('BOT_TOKEN')

format_string = "%Y-%m-%dT%H:%M:%S.%f%z"

# Create bot instance
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

if len(VIEW_USER_IDS) != len(SEND_CHANNEL_IDS):
    print(f"VIEW_USER_IDS: {VIEW_USER_IDS}")
    print(f"SEND_CHANNEL_IDS: {SEND_CHANNEL_IDS}")
    raise ValueError("VIEW_USER_IDS and SEND_CHANNEL_IDS must have the same length")
user_channel_map = dict(zip(map(str, VIEW_USER_IDS), SEND_CHANNEL_IDS))


async def retrieve_messages(channel_id, last_message_id=None) -> list[dict]:
    headers = {
        'authorization' : AUTH_TOKEN
    }
    if not last_message_id:
        req = requests.get(f'{API_ENDPOINT}/channels/{channel_id}/messages?limit=50', headers=headers)
    else:
        req = requests.get(f'{API_ENDPOINT}/channels/{channel_id}/messages?limit=50&before={last_message_id}', headers=headers)
    if req.status_code == 401:
        print("Unauthorized")
        return []
    json_data = json.loads(req.text)
    return json_data
            
def filter_messages(messages) -> list[dict]:
    list_of_dict_messages = []
    for message in messages:
        dict_messages = {}
        timestamp, author_id, content, id, author = message.get('timestamp'), message.get('author').get('id'), message.get('content'), message.get('id'), message.get('author').get('username')
        dict_messages['timestamp'] = timestamp
        dict_messages['id'] = id
        dict_messages['author'] = author
        dict_messages['author_id'] = author_id
        dict_messages['content'] = content
        dict_messages['avatar'] = message.get('author').get('avatar')
        list_of_dict_messages.append(dict_messages)
    return list_of_dict_messages

def filter_by_author(messages, user_ids) -> dict[str, list[dict]]:
    """
    Filter messages and group them by author
    
    Args:
        messages: List of message dictionaries
        user_ids: List of user IDs to filter by
    
    Returns:
        Dictionary with user IDs as keys and their respective messages as values
    """
    filtered_messages = {str(user_id): [] for user_id in user_ids}
    
    for msg in messages:
        author_id = msg['author_id']
        if author_id in map(str, user_ids):
            filtered_messages[author_id].append(msg)
    
    return filtered_messages

async def random_delay() -> float:
    """Creates a random delay between 1 second and 3 hours"""
    delay = random.uniform(1, 3*60*60)
    print(f"Waiting for {delay:.2f} seconds before next execution")
    await asyncio.sleep(delay)
    
    return delay

@tasks.loop(hours=6, minutes=1)  # Base interval, we'll add randomization
async def periodic_task():
    """Background task that runs every 1 minute"""
    try:
        channel_id = VIEW_CHANNEL_ID
        channels = await get_channels(SEND_CHANNEL_IDS)
        old_last_message = await get_last_user_message(channels[0], bot.user.id)
        if old_last_message and old_last_message.content.startswith('Last message ID: '):
            target_id = int(old_last_message.content.split(': ')[1])
        else:
            target_id = None
        
        if not target_id:
            target_id = None
        messages = await retrieve_messages_until_id(channel_id, target_id)
        messages = filter_messages(messages)
        messages_by_user = filter_by_author(messages, VIEW_USER_IDS)
        # Get the channel to send messages to
        
        if not channels:
            print("Could not find the specified channel")
            return

        # Send messages for each user
        for user_id, user_messages in messages_by_user.items():
            send_channel = bot.get_channel(user_channel_map[user_id])
            if user_messages:
                user_name = user_messages[0]['author']
                avatar = user_messages[0]['avatar']
                user_messages = [msg['content'] for msg in user_messages]
                user_messages = user_messages[::-1]
                user_messages = '\n'.join(user_messages)
                embed = discord.Embed(
                    title=f"{user_name} Messages",
                    colour=discord.Colour.blue(),
                    timestamp=datetime.now()
                )
                embed.add_field(name=f'', value=f'{user_messages}')
                embed.set_author(name=f'{user_name}', icon_url=f'https://cdn.discordapp.com/avatars/{user_id}/{avatar}.png')
                await send_channel.send(embed=embed)
                await send_channel.send(f'Last message ID: {messages[0]["id"]}')
            else:
                await send_channel.send(f'No messages found for user {user_id}')
                await send_channel.send(f'Last message ID: {messages[0]["id"]}')
        
        
        # Wait for random delay before next iteration
        await random_delay()
        
    except Exception as e:
        print(f"Error in periodic task: {str(e)}")

@periodic_task.before_loop
async def before_periodic_task():
    """Wait until the bot is ready before starting the task"""
    await bot.wait_until_ready()

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    periodic_task.start()  # Start the periodic task when bot is ready

@bot.command(name='send')
async def send_message(ctx, *, message):
    """Send a message to a specific channel
    Usage: !send Your message here
    """
    channel = bot.get_channel(int(SEND_CHANNEL_IDS))  
    if channel:
        await channel.send(message)
        await ctx.send(f'Message sent to channel: {channel.name}')
    else:
        await ctx.send('Could not find the specified channel')

async def retrieve_messages_until_id(channel_id, target_message_id, before_id=None, collected_messages=None, iteration=0) -> list[dict]:
    """
    Recursively retrieve messages until reaching a specific message ID or max iterations
    
    Args:
        channel_id: The Discord channel ID to fetch messages from
        target_message_id: The message ID to stop at (inclusive)
        before_id: Message ID to fetch messages before
        collected_messages: List to store collected messages
        iteration: Current iteration count
    
    Returns:
        List of messages from newest to target message ID
    """
    MAX_ITERATIONS = 20

    
    if collected_messages is None:
        collected_messages = []
    
    if iteration >= MAX_ITERATIONS:
        print(f"Reached maximum iterations ({MAX_ITERATIONS}). Stopping.")
        return collected_messages
    
    # Add random delay between 0.25 and 1 second between API calls
    if iteration > 0:  # Skip delay on first call
        await asyncio.sleep(random.uniform(0.25, 1))
    
    # Get batch of messages
    messages = await retrieve_messages(channel_id, before_id)
    
    if not messages:  # No more messages to fetch
        return collected_messages
    
    for message in messages:
        if target_message_id is not None and int(message['id']) <= int(target_message_id):
            # We've reached or passed our target message
            collected_messages.extend([msg for msg in messages if int(msg['id']) >= int(target_message_id)])
            return collected_messages
        
    collected_messages.extend(messages)
    
    # Recursively get more messages, using the last message's ID as before_id
    last_message_id = messages[-1]['id']
    return await retrieve_messages_until_id(channel_id, target_message_id, last_message_id, collected_messages, iteration + 1)

async def get_last_user_message(channel, user_id) -> discord.Message:
    """
    Retrieve the last message from a specific user in a channel
    
    Args:
        channel: discord.Channel object to search in
        user_id: The user ID to find messages for
    
    Returns:
        discord.Message object of the last message, or None if no message found
    """
    async for message in channel.history(limit=100):
        if str(message.author.id) == str(user_id):
            return message
            
    return None

@bot.command(name='fetch')
async def fetch_messages(ctx: commands.Context):
    """
    Command to fetch messages until a specific message ID
    Usage: !fetch <message_id>
    """
    channel_id = VIEW_CHANNEL_ID
    channels = await get_channels(SEND_CHANNEL_IDS)
    old_last_message = await get_last_user_message(channels[0], bot.user.id)
    if old_last_message:
        target_id = int(old_last_message.content.split(': ')[1])
    else:
        target_id = None
    try:
        messages = await retrieve_messages_until_id(channel_id, target_id)
        messages = filter_messages(messages)
        messages_by_user = filter_by_author(messages, VIEW_USER_IDS)
        
        
        # Send messages for each user
        for user_id, user_messages in messages_by_user.items():
            send_channel = bot.get_channel(user_channel_map[user_id])
            if user_messages:
                user_name = user_messages[0]['author']
                avatar = user_messages[0]['avatar']
                user_messages = [msg['content'] for msg in user_messages]
                user_messages = user_messages[::-1]
                user_messages = '\n'.join(user_messages)
                embed = discord.Embed(
                    title=f"{user_name} Messages",
                    colour=discord.Colour.blue(),
                    timestamp=datetime.now()
                )
                embed.add_field(name=f'', value=f'{user_messages}')
                embed.set_author(name=f'{user_name}', icon_url=f'https://cdn.discordapp.com/avatars/{user_id}/{avatar}.png')
                await send_channel.send(embed=embed)
                await send_channel.send(f'{messages[0]["id"]}')
            else:
                await send_channel.send(f'No messages found for user {user_id}')
    except Exception as e:
        await ctx.send(f'Error fetching messages: {str(e)}')

async def get_channels(channel_ids) -> list[discord.TextChannel]:
    """
    Retrieve channel information for a list of channel IDs using discord.py
    
    Args:
        channel_ids: List of channel IDs to fetch
    
    Returns:
        List of discord.TextChannel objects
    """
    channels = []
    for channel_id in channel_ids:
        try:
            channel = bot.get_channel(int(channel_id))
            if channel:
                channels.append(channel)
            else:
                print(f"Could not find channel with ID: {channel_id}")
        except Exception as e:
            print(f"Error fetching channel {channel_id}: {str(e)}")
            continue
            
    return channels

def main():
    bot.run(BOT_TOKEN)

if __name__ == "__main__":
    main()

