import asyncio, hashlib, sys, os, requests, re, time
from telethon import TelegramClient, events, errors
from datetime import datetime
import uuid
import platform

# --- 🎨 COLORS ---
G, Y, R, C, W, B = '\033[92m', '\033[93m', '\033[91m', '\033[96m', '\033[0m', '\033[1m'

# --- 🔐 CONFIGURATION ---
RAW_LINK = "https://raw.githubusercontent.com/ASYASIRARAFAT/x-snaiper-pro/main/approved.txt?"
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
min_bal = 1.0   
max_bal = 30.0
# এই লিস্টটি যোগ করতে ভুলবেন না (ফাংশনগুলোর বাইরে থাকবে এটি)
APPROVED_BINS = ["461126", "403446", "491277", "435880", "511332", "533985", "451129"]
click_lock = asyncio.Lock()

# --- MATCHING ENGINE ---
def find_target_btn(msg):
    if not msg or not msg.buttons: return None, None # পরিবর্তন ১: দুটি None রিটার্ন
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
                if "purchase" in btn.text.lower(): return btn, target # পরিবর্তন ২: বাটন এবং টার্গেট দুটিই রিটার্ন
    return None, None # পরিবর্তন ৩: দুটি None রিটার্ন

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
# --- STOCK LISTENER ---
@client.on(events.NewMessage(chats=STOCK_CHANNEL_ID))
async def stock_listener(event):
    global targets, is_attacking
    text = event.raw_text
    
    # ডাটা এক্সট্রাক্ট করা (BIN এবং Balance)
    bin_match = re.search(r'Card BIN:\s*(\d{6})', text, re.IGNORECASE)
    bal_match = re.search(r'Balance:.*?\$(\d+\.\d+)', text, re.IGNORECASE)
    
    # কন্ডিশন চেক করার জন্য ডাটা বের করা
    paypal_no = re.search(r'Used PayPal:\s*No', text, re.IGNORECASE)
    google_no = re.search(r'Used Google:\s*No', text, re.IGNORECASE)
    reg_false = re.search(r'Registered:\s*false', text, re.IGNORECASE)
    reg_true = re.search(r'Registered:\s*True', text, re.IGNORECASE)

    if bin_match and bal_match:
        t_bin = bin_match.group(1)
        t_bal = float(bal_match.group(1))

        # ---  Approved BIN ফিল্টার ---
        if t_bin not in APPROVED_BINS:
            log(f"Skipped: BIN {t_bin} is not in Approved List", "wait")
            return

        # --- নতুন ফিল্টার লজিক ---
        if not (min_bal <= t_bal <= max_bal):
            log(f"Skipped: ${t_bal} is out of range ({min_bal}-{max_bal})", "wait")
            return # রেঞ্জের বাইরে হলে এখানেই থেমে যাবে, টার্গেটে অ্যাড হবে না

        should_add = False

        if t_bal > 30.0:
            log(f"Over Budget Ignored: {t_bin} (${t_bal})", "wait")
            return

        # ১. Google: No হতে হবে (এটি বাধ্যতামূলক)
        if google_no:
            # ২. Registered: false হলে সরাসরি অ্যাড (PayPal No/Yes যাই হোক)
            if reg_false:
                should_add = True
            
            # ৩. Registered: True হলে ব্যালেন্স ১৭ এর কম হতে হবে
            elif reg_true and paypal_no:
                if t_bal < 17.0:
                    should_add = True
                else:
                    log(f"Ignored (High Bal Reg:True): {t_bin} (${t_bal})", "wait")

        # টার্গেট অ্যাড করার প্রক্রিয়া
        # টার্গেট অ্যাড করার প্রক্রিয়া
        if should_add:
            if not any(t['bin'] == t_bin and t['bal'] == str(t_bal) for t in targets):
                targets.append({
                    'bin': t_bin, 
                    'bal': str(t_bal), 
                    'added_at': time.time() 
                })
                # নতুন লাইন: সিরিয়াল নম্বর বের করে লগে দেখানো
                serial_num = len(targets)
                log(f"Auto-Target Added [Serial: {serial_num}]: {t_bin} (${t_bal})", "target")
                
                if not is_attacking:
                    is_attacking = True
                    log("Stock Alert! Sniper Activated.", "success")
        else:
            # যদি কন্ডিশন না মেলে তবে কেন অ্যাড হলো না তার লগ (অপশনাল)
            if not google_no:
                log(f"Ignored (Google:Yes): {t_bin}", "error")



# --- COMMANDS ---
@client.on(events.NewMessage(outgoing=True, chats=BOT_USERNAME))
async def command(event):
    global targets, is_attacking, min_bal, max_bal # এই লাইনটি আপডেট করুন
    txt = event.raw_text.strip()

    # ১. পুরো স্টক মেসেজ থেকে অটো-এক্সট্রাক্ট লজিক
    if "card bin" in txt.lower() and "balance" in txt.lower():
        bin_match = re.search(r'Card BIN:\s*(\d{6})', txt, re.IGNORECASE)
        bal_match = re.search(r'Balance:.*?\$\s*(\d+\.\d+)', txt, re.IGNORECASE)

        if bin_match and bal_match:
            t_bin = bin_match.group(1)
            t_bal = bal_match.group(1)
            
            targets.append({
                'bin': t_bin, 
                'bal': t_bal, 
                'wait': 0,
                'added_at': time.time() 
            })
            
            is_attacking = True
            # নতুন লাইন: সিরিয়াল নম্বর বের করে লগে দেখানো
            serial_num = len(targets)
            log(f"Manual Extract [Serial: {serial_num}]: {t_bin} (${t_bal})", "target")
            
            # --- ডিলিট লজিক শুরু ---
            # আগে রিপ্লাই মেসেজটি পাঠিয়ে ভেরিয়েবলে সেভ করা
            reply = await event.respond(f"🎯 **Target Locked!**\nBIN: `{t_bin}`\nBalance: `${t_bal}`\n\n🚀 Sniper is now **ACTIVE**.")
            
            await asyncio.sleep(5) # ৫ সেকেন্ড অপেক্ষা
            try:
                await event.delete()   # আপনার পাঠানো বড় মেসেজ ডিলিট
                await reply.delete()   # বটের রিপ্লাই মেসেজ ডিলিট
            except: pass # কোনো কারণে ডিলিট না হলে এরর দেবে না
            # --- ডিলিট লজিক শেষ ---
        else:
            await event.reply("❌ Failed to extract BIN or Balance.")
# ২. অন্যান্য কন্ট্রোল কমান্ডসমূহ
    else:
        cmd = txt.lower()
        # এখানে set যোগ করা হয়েছে যাতে মেসেজ অটো ডিলিট হয়
        if cmd in ["targets", "status", "clear", "stop"] or cmd.startswith("cancel") or cmd.startswith("set"):
            await event.delete() 
            
            if cmd == "targets":
                if not targets:
                    await event.respond("❌ No targets in memory.", delete_after=5)
                else:
                    msg = "🎯 **Active Targets List:**\n"
                    for i, t in enumerate(targets, 1):
                        msg += f"{i}. BIN: `{t['bin']}` | Bal: `${t['bal']}`\n"
                    await event.respond(msg, delete_after=10)

            elif cmd.startswith("cancel"):
                try:
                    parts = cmd.split()
                    index = int(parts[1]) - 1
                    if 0 <= index < len(targets):
                        removed = targets.pop(index)
                        await event.respond(f"✅ Target {index + 1} Removed: `{removed['bin']}`", delete_after=5)
                        if not targets:
                            is_attacking = False
                    else:
                        await event.respond("❌ Invalid serial number!", delete_after=5)
                except:
                    await event.respond("Format: `cancel 1`", delete_after=5)

            elif cmd == "status":
                state = "🔥 ACTIVE" if is_attacking else "💤 SLEEPING"
                # এখানে ব্যালেন্স রেঞ্জ ফিল্টারটি যোগ করা হয়েছে
                await event.respond(f"📊 **System Status:** {state}\n📦 **Targets:** {len(targets)}\n💰 **Range:** `${min_bal}` - `${max_bal}`", delete_after=5)
            
            # clear কমান্ডের মিসিং লজিক এখানে অ্যাড করা হলো
            elif cmd == "clear":
                targets.clear()
                is_attacking = False
                await event.respond("🧹 Memory Cleared. Sniper Stopped.", delete_after=5)

            elif cmd.startswith("set"):
                try:
                    parts = cmd.split()
                    # এখান থেকে global লাইনটি মুছে ফেলা হয়েছে
                    min_bal = float(parts[1])
                    max_bal = float(parts[2])
                    await event.respond(f"✅ Auto-Filter Updated!\nRange: `${min_bal}` to `${max_bal}`", delete_after=5)
                    log(f"Range Updated: {min_bal} - {max_bal}", "success")
                except:
                    await event.respond("Format: `set MIN MAX` (e.g., `set 5 20`)", delete_after=5)

            elif cmd == "stop":
                is_attacking = False
                await event.respond("🛑 Sniper Engine Paused.", delete_after=5)

# --- BOT HANDLER ---
@client.on(events.NewMessage(chats=BOT_USERNAME))
@client.on(events.MessageEdited(chats=BOT_USERNAME))
async def handler(event):
    if not is_attacking or not event.message.buttons: return 

    msg_text = event.message.text or ""
    if "listings" not in msg_text.lower() and "total cards" not in msg_text.lower():
        return

    btn, target_obj = find_target_btn(event.message) # এখানে দুটি ভ্যালু রিসিভ করছি
    if btn and target_obj:
        asyncio.create_task(attack(btn))

        if target_obj in targets:
            targets.remove(target_obj) # টার্গেটটি লিস্ট থেকে ডিলিট করে দিচ্ছি
            log(f"Target Removed from memory: {target_obj['bin']}", "wait")
            

            # --- AUTO-CLEANUP ENGINE ---
async def auto_cleanup():
    while True:
        try:
            now = time.time()
            # targets[:] ব্যবহার করা হয়েছে যাতে লুপ চলাকালীন লিস্ট থেকে আইটেম ডিলিট করলে এরর না আসে
            for target in targets[:]: 
                # ১৮০ সেকেন্ড = ৩ মিনিট
                # যদি টার্গেট অ্যাড হওয়ার সময় থেকে বর্তমান সময়ের পার্থক্য ১৮০ সেকেন্ডের বেশি হয়
                if now - target.get('added_at', now) > 180:
                    targets.remove(target)
                    log(f"Auto-Expired: {target['bin']} (3 mins passed)", "error")
            
            # প্রতি ১০ সেকেন্ড পরপর মেমরি চেক করবে
            await asyncio.sleep(10)
        except Exception as e:
            # কোনো এরর হলে ১০ সেকেন্ড পর আবার চেষ্টা করবে
            await asyncio.sleep(10)
        

# --- START ---
async def main():
    ui_header()
    if not verify_user(): sys.exit() 
        
    log("Connecting to Telegram...", "wait")
    await client.start()

    # --- ⚡ ব্যাকগ্রাউন্ডে অটো-ক্লিনআপ শুরু ---
    asyncio.create_task(auto_cleanup())

    ui_header()
    log(f"X-Sniper Ready | HWID: {get_hwid()}", "success")
    log(f"Monitoring Stock ID: {STOCK_CHANNEL_ID}", "info")
    await client.run_until_disconnected()

if __name__ == "__main__":
    client.loop.run_until_complete(main())
