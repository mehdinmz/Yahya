# Yahya - Telegram Group Message Hunter 🤖

**Yahya** is a minimalist Telegram userbot built with [Telethon](https://github.com/LonamiWebs/Telethon)  
that extracts messages sent by a specific user from group chats — in real time.

Originally developed during my second semester of university to manage the overwhelming volume of group messages  
(and avoid missing important posts from professors, admins, or active classmates).

---

## 🚀 What does Yahya do?

Given:
- A **Telegram group invite link**
- A **target username** 

Yahya will:
- Join the group
- Monitor incoming messages live
- Forward messages from the target user to your personal chat

⚠️ Yahya does **not** access historical messages. It only watches what's posted **after it joins.**

---

## ⚙️ Why did I build this?

University group chats are a mess. Important messages often get buried under irrelevant chatter.  
I needed a tool that would:
- Extract messages from key individuals (like professors or organizers)
- Keep me focused without being glued to my phone
- Give me peace of mind that I wouldn't miss anything critical

Also, building weird little tools is therapy 🧠

---

## 📦 Setup

### 🔧 Requirements
- Python 3.8+
- A Telegram account
- [Telethon](https://github.com/LonamiWebs/Telethon)

### 🔑 How to get your `API_ID` and `API_HASH`

1. Go to [my.telegram.org](https://my.telegram.org)
2. Log in with your Telegram number
3. Click on **API Development Tools**
4. Choose a name for your app (e.g., `yahya-bot`) and leave the URL fields blank or use `http://localhost`
5. You'll get:
   - `API_ID` (a 6-7 digit number)
   - `API_HASH` (a long alphanumeric string)

Copy these into the `APIrequirements.py` file.

---
## 🧰 Installing & Running Yahya

### 1. Clone the repository

```bash
git clone https://github.com/mehdinmz/Yahya.git
cd Yahya
```
### 2. Create a virtual environment (recommended) 
```bash
python -m venv .venv
```
### 3. Activate the virtual environment
**Windows:**
```bash
.venv\Scripts\activate
```
**Mac/Linux:**
```bash
source .venv/bin/activate
```
### 4. Install requirements
```bash
pip install -r requirements.txt
```
### 5. Configure the bot

Open `APIrequirements.py` and set the following:

```python
API_ID = 'your_api_id'
API_HASH = 'your_api_hash'
```
### 6. Run the bot
 ```bash
python main.py
```
## 🙋‍♂️ How to Use
1. Search bot’s username in Telegram 
2. Open the chat
3. Send the `/start` command once
4. Send the `/newtarget` command to add target
5. Send the target's @username and the group invite link
### After that, Yahya will:
- Join the specified group
- Watch messages in real time
- Forward any message from the target user to you directly

**💡 Use the `/help` command to see all available options and usage examples.**
## 🛡️ Ethics & Boundaries

This project is intended for personal productivity use only.  
Please avoid using Yahya in a way that violates privacy, consent, or community guidelines.

- Do **not** monitor individuals without their knowledge and approval.
- Do **not** use this tool in any malicious or intrusive way.
- Always respect Telegram’s [Terms of Service](https://telegram.org/tos).

Yahya was created to reduce message clutter and help users focus — not to facilitate surveillance or harassment.
## 🧠 Final Note
*"If your brain can't filter the chaos, build something that does." – M*

## 📬 Questions?
Open an issue or DM me on Telegram: [@Hajmehdipv]
