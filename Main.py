#libraries
from telethon import TelegramClient,events
from APIrequirements import API_ID,API_hash
from telethon.tl.custom.message import Message
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
import logging
import json
import os
# log
logging.basicConfig(format='[%(levelname) %(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
#save&load_data_func
DATA_FILE = "user_data.json"
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# set-up client
client = TelegramClient(session=".session",
                api_hash=API_hash,api_id=API_ID)
# manage users
user_data = load_data() # { user_id: { "gap_list": [], "target_list": [] } }
user_stats = {}
print(user_data)

#start
@client.on(events.NewMessage(pattern="/start",func= lambda e : e.is_private))
async def start_chat(event:Message):
    user_id = event.sender_id
    if user_id not in user_data:
        user_data[user_id] = {"gap_list": [], "target_list": []}
        save_data(user_data)
        print("new user!!!!!!!!")
    await event.respond("Wellcome to Monitoring Bot. \n Use /help to show commands")

#help
@client.on(events.NewMessage(pattern="/help",func= lambda e : e.is_private))
async def help(event:Message):
    await event.respond("/new_target - Add a new target user \n /load_targets - View all added targets \n /delete_target - Remove an existing target")

#loadtargets
@client.on(events.NewMessage(pattern="/load_targets",func= lambda e : e.is_private))
async def load_user(event:Message):
     user_id = event.sender_id
     targets = user_data.get(user_id, {}).get("target_list", [])
     if targets == []:
        await event.respond("You have no targets yet.")
     else:
         await event.respond(f"Your targets:{targets}")

#new_target
@client.on(events.NewMessage(pattern="/new_target",func= lambda e : e.is_private))
async def get_target(event:Message):
    user_id = event.sender_id
    await event.respond("Enter Target UserName(@example)")
    user_stats[user_id]="adding target"
    # save_data(user_data)


@client.on(events.NewMessage(pattern="@",func= lambda e : e.is_private))
async def add_target(event:Message):
    user_id = event.sender_id
    mssg = event.text.strip()
    target_id = await client.get_entity(mssg.replace("@",""))
    print(target_id.id)
    if user_stats[user_id] == "adding target":
        user_data[user_id]["target_list"].append(target_id.id)
        save_data(user_data)
        user_stats[user_id]= "group target"
        await event.respond("Enter Target Group(t.me/example)")
    elif user_stats[user_id]=="delete target":
        if target_id.id in user_data.get(user_id, {}).get("target_list", []):
            user_data[user_id]["target_list"].remove(target_id.id)
            save_data(user_data)
            await event.respond("Target removed.")
        else:
            await event.respond("Target not found in your list.You can add one!")
        user_stats[user_id]=""


@client.on(events.NewMessage(pattern="t.me",func= lambda e : e.is_private))
async def add_group(event:Message):
    user_id = event.sender_id
    mssg = event.text.strip()
    if user_stats[user_id] == "group target":
        group_id = mssg.replace("t.me/","")
        if group_id.startswith("+"):
            group_id = group_id.replace("+","")
            try:
                await client(request=ImportChatInviteRequest(group_id))
            except Exception as e:
                logging.warning(f"Could not join group {group_id}: {e}")
        else:
            try:
                await client(request=JoinChannelRequest(group_id))
                
            except Exception as e:
                logging.warning(f"Could not join group {group_id}: {e}")
        await event.respond("Target Added")
        group_ID_n = await client.get_entity(group_id)
        print(group_ID_n.id)
        user_data[user_id]["gap_list"].append(group_ID_n.id)
        user_stats[user_id]=""
        save_data(user_data)
        

#deletetarget
@client.on(events.NewMessage(pattern="/delete_target",func= lambda e : e.is_private))
async def delete_user(event:Message):
    user_id = event.sender_id
    await event.respond(message="Send ID to remove(@example)")
    user_stats[user_id]="delete target"


#handle gap
@client.on(event=events.NewMessage(func=lambda e: e.is_group))
async def forward_target_message(event:Message):
    tar_id = event.sender_id
    for user_id, data in user_data.items():
        if tar_id in data["target_list"]:
            try:
                if event.is_reply:
                    rr = await event.get_reply_message()
                    print(rr)
                    await client.forward_messages(entity=user_id,messages=rr,from_peer=event.chat_id,silent=True)
                await client.forward_messages(entity=user_id,messages=event.message,from_peer=event.chat_id,silent=True)
            except Exception as e:
                logging.warning(f" Error handling message: {e}")

#running bot
client.start()
client.run_until_disconnected()