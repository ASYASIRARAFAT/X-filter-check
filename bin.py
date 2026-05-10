import asyncio, hashlib, sys, os, requests, re, time
from telethon import TelegramClient, events, errors
from datetime import datetime

# --- 🎨 COLORS ---
G, Y, R, C, W, B = '\033[92m', '\033[93m', '\033[91m', '\033[96m', '\033[0m', '\033[1m'

# --- 🔐 CONFIGURATION ---
RAW_LINK = "https://raw.githubusercontent.com/ASYASIRARAFAT/x-sniper-bot/main/approved.txt?"
BOT_USERNAME = 'XPrepaidsExchangeBot'
STOCK_CHANNEL_ID = -1003280015883  # আপনার দেওয়া স্টক চ্যানেল আইডি

def get_hwid():
    try:
        # Termux/Linux এর জন্য ইউনিক আইডি জেনারেট করা
        cpu = os.popen('uname -a').read()
        user = os.popen('whoami').read()
        return hashlib.sha256((cpu + user).encode()).hexdigest()[:12].upper()
    except:
        return "9FDF6C1387E7"

# --- 🛠 UI & LOGGING ---
def ui_header():
    os.system('clear' if os.name == 'posix' else 'cls')
    print(f"{C}{B}╔══════════════════════════════════════════════════════════╗")
    print(f"║                      {W}{B}X-SNIPER v21.0{C}{B}                      ║")
    print(f"║             {Y}SECURED MULTI-TARGET SNIPER ENGINE{C}{B}           ║")
    print(f"║             {G}Developed By: Yasir Arafat{C}{B}                   ║")
    print(f"╚══════════════════════════════════════════════════════════╝{W}")

def log(msg, type="info"):
    now = datetime.now().strftime("%H:%M:%S")
    if type == "success": print(f"{G}[{now}] [✔] {msg}{W}")
    elif type == "error": print(f"{R}[{now}] [✘] {msg}{W}")
    elif type == "target": print(f"{C}[{now}] [🎯] {msg}{W}")
    elif type == "wait": print(f"{Y}[{now}] [•] {msg}{W}")
    else: print(f"{W}[{now}] [ℹ] {msg}{W}")

# --- 🛡️ VERIFICATION ENGINE ---
def verify_user():
    uid = get_hwid()
    log(f"Checking HWID: {uid}", "wait")
    try:
        res = requests.get(RAW_LINK, timeout=10).text
        if uid in res:
            log("Access Granted! Welcome Commander.", "success")
            time.sleep(1)
            return True
        else:
            log("Access Denied! Hardware ID not registered.", "error")
            print(f"{Y}\nYour ID: {uid}{W}")
            print(f"{C}Contact Yasir Arafat to register your HWID.{W}")
            return False
    except:
        log("Connection Error! Unable to verify ID.", "error")
        return False

# --- ⚙️ API SETUP ---
def load_config():
    if os.path.exists("config.txt"):
        with open("config.txt", "r") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            if len(lines) >= 2:
                return int(lines[0]), lines[1]
    
    ui_header()
    log("Enter API details to continue:", "wait")
    api_id = input(f"{C}Enter API ID: {W}").strip()
    api_hash = input(f"{C}Enter API Hash: {W}").strip()
    with open("config.txt", "w") as f:
        f.write(f"{api_id}\n{api_hash}")
    return int(api_id), api_hash

API_ID, API_HASH = load_config()
client = TelegramClient('v21_session', API_ID, API_HASH)

# --- GLOBAL STATE ---
targets = [] 
is_attacking = False
click_lock = asyncio.Lock()

# --- MATCHING ENGINE ---
def find_target_btn(msg):
    if not msg or not msg.buttons: return None
    BAD_SIGNS = ["🅶", "🅿️", "used", "relister", "❌"]
    flat_buttons = [btn for row in msg.buttons for btn in row]

    for target in targets:
        t_bin = target['bin'].lower()
        t_bal = target['bal'].replace('$', '').lower()
        
        found_index = None
        for i, btn in enumerate(flat_buttons):
            btn_txt = btn.text.replace(' ', '').replace('$', '').lower()
            if t_bin in btn_txt and t_bal in btn_txt:
                if any(sign in btn.text for sign in BAD_SIGNS): continue
                found_index = i
                log(f"Match Found: {btn.text}", "success")
                break

        if found_index is not None:
            for btn in flat_buttons[found_index:]:
                if "purchase" in btn.text.lower(): return btn
    return None

# --- EXECUTION ---
async def attack(btn):
    global is_attacking
    log("TARGET SPOTTED! EXECUTING PURCHASE...", "target")
    async with click_lock:
        for i in range(2):
            try:
                await btn.click()
                log(f"Click {i+1} Sent Successfully", "success")
                await asyncio.sleep(0.2)
            except Exception as e: log(f"Click Error: {e}", "error")
    # কেনার পর ওই টার্গেটের কাজ শেষ
    is_attacking = False 

# --- STOCK LISTENER ---
@client.on(events.NewMessage(chats=STOCK_CHANNEL_ID))
async def stock_listener(event):
    global targets, is_attacking
    text = event.raw_text
    
    # আপনার ফরম্যাট অনুযায়ী BIN (৬ ডিজিট) এবং Balance বের করা
    bin_match = re.search(r'BIN:\s*(\d{6})', text, re.IGNORECASE)
    bal_match = re.search(r'Balance:.*?\$(\d+\.\d+)', text, re.IGNORECASE)

    if bin_match and bal_match:
        t_bin = bin_match.group(1)
        t_bal = bal_match.group(1)
        
        # নতুন টার্গেট অ্যাড করা
        if not any(t['bin'] == t_bin and t['bal'] == t_bal for t in targets):
            targets.append({'bin': t_bin, 'bal': t_bal, 'wait': 0})
            log(f"Auto-Target Added: {t_bin} (${t_bal})", "target")
            
            # অটো অ্যাটাক মোড অন
            if not is_attacking:
                is_attacking = True
                log("Stock Alert! Sniper Activated.", "success")

# --- COMMANDS ---
@client.on(events.NewMessage(outgoing=True, chats=BOT_USERNAME))
async def command(event):
    global targets, is_attacking
    txt = event.raw_text.lower().strip()

    if txt.startswith("buy"):
        try:
            parts = txt.split()
            targets.append({'bin': parts[1], 'bal': parts[2], 'wait': int(parts[3])})
            log(f"Manual Target: {parts[1]} (${parts[2]})", "target")
        except: log("Format: buy 511332 50.00 0", "error")

    elif txt == "confirm":
        is_attacking = True
        log("Manual Engine Start!", "success")

    elif txt == "clear":
        targets = []
        is_attacking = False
        log("Targets Cleared.", "error")

# --- BOT HANDLER ---
@client.on(events.NewMessage(chats=BOT_USERNAME))
@client.on(events.MessageEdited(chats=BOT_USERNAME))
async def handler(event):
    if not is_attacking or not event.message.buttons: return 

    msg_text = event.message.text or ""
    if "listings" not in msg_text.lower() and "total cards" not in msg_text.lower():
        return

    btn = find_target_btn(event.message)
    if btn:
        asyncio.create_task(attack(btn))

# --- START ---
async def main():
    ui_header()
    if not verify_user(): sys.exit()
        
    log("Connecting to Telegram...", "wait")
    await client.start()
    ui_header()
    log(f"X-Sniper Ready | HWID: {get_hwid()}", "success")
    log(f"Monitoring Stock ID: {STOCK_CHANNEL_ID}", "info")
    await client.run_until_disconnected()

if __name__ == "__main__":
    client.loop.run_until_complete(main())
