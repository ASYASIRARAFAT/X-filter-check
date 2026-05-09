# --- 📡 STOCK CONFIG ---
STOCK_CHANNEL = '@Your_Channel_Username' # এখানে আপনার চ্যানেলের ইউজারনেম দিন

@client.on(events.NewMessage(chats=STOCK_CHANNEL))
async def stock_listener(event):
    global targets, is_attacking
    text = event.raw_text
    
    # ১. BIN বের করা (৫১১৩৩২xx থেকে শুধু ৫১১৩৩২ নিবে)
    bin_match = re.search(r'Card BIN:\s*(\d{6})', text, re.IGNORECASE)
    
    # ২. ব্যালেন্স বের করা ($50.00 থেকে শুধু 50.00 নিবে)
    bal_match = re.search(r'Balance:.*?\$(\d+\.\d+)', text, re.IGNORECASE)

    if bin_match and bal_match:
        t_bin = bin_match.group(1)
        t_bal = bal_match.group(1)
        
        # ডুপ্লিকেট চেক: যদি অলরেডি এই টার্গেট অ্যাড করা থাকে তবে আর অ্যাড করবে না
        if not any(t['bin'] == t_bin and t['bal'] == t_bal for t in targets):
            # wait টাইম ০ দিয়ে অ্যাড করা হচ্ছে
            targets.append({'bin': t_bin, 'bal': t_bal, 'wait': 0})
            
            log(f"Auto-Target Added: {t_bin} (${t_bal})", "target")
            
            # অটোমেটিক অ্যাটাক মোড চালু করা
            if not is_attacking:
                is_attacking = True
                log("Stock Found! Sniper Engine Activated.", "success")
