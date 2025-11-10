# ⚡ სწრაფი დაწყება - 30 წუთში!

ეს არის კონცენტრირებული ვერსია დაყენებისთვის. დეტალური ინსტრუქციები იხილე `README.md`-ში.

---

## 🎯 3 მთავარი ნაბიჯი

### 1️⃣ API Keys მიღება (10 წთ)

**Claude API:**
1. https://console.anthropic.com/ → Login
2. Billing → დაამატე ბარათი
3. API Keys → Create → კოპირება

**Telegram Bot:**
1. Telegram → @BotFather → `/newbot`
2. სახელი: `Nika Parenting Bot`
3. Username: `nika_parenting_bot`
4. TOKEN კოპირება

---

### 2️⃣ Render.com Setup (15 წთ)

1. https://render.com/ → Sign Up (GitHub)
2. New + → Web Service
3. Public Git Repository → გადადი შემდეგ ნაბიჯზე (ან GitHub repo-ს upload)

**Settings:**
```
Name: tiktok-parenting-bot
Runtime: Python 3
Build: pip install -r requirements.txt
Start: python bot.py
```

**Environment Variables** (ყველა ერთდროულად დაამატე):
```
ANTHROPIC_API_KEY=sk-ant-api03-შენი_გასაღები
TELEGRAM_BOT_TOKEN=1234567890:შენი_ტოკენი
TIMEZONE=Asia/Tbilisi
GENERATION_HOUR=13
GENERATION_MINUTE=0
NEWS_CHECK_DAYS=0,3
LEARNING_PHASE_DAYS=14
LEARNING_VARIANTS=6
NORMAL_VARIANTS=3
```

4. Create Web Service → დაელოდე 5-10 წთ

---

### 3️⃣ Chat ID + Test (5 წთ)

1. Telegram → შენი bot → `/start`
2. Render → Logs → დაკოპირე Chat ID
3. Render → Environment → Add:
   ```
   ADMIN_CHAT_ID=შენი_chat_id
   ```
4. Manual Deploy

**Test:**
```
/generate
```

---

## ✅ Checklist

- [ ] Claude API Key აქვს
- [ ] Telegram Bot Token აქვს
- [ ] Render.com account შექმნილი
- [ ] Environment Variables დამატებული (9 ცალი)
- [ ] Bot deployed და "Live"
- [ ] Chat ID დამატებული
- [ ] /start მუშაობს
- [ ] /generate მუშაობს

---

## 🆘 სწრაფი პრობლემების გადაჭრა

**Bot არ პასუხობს:**
→ Render Logs შემოწმება

**Chat ID არ ჩანს:**
→ Render Logs → Real-time ჩართვა → /start თავიდან

**Claude API error:**
→ https://console.anthropic.com/ → შემოწმება balance

**"Live" მაგრამ არ მუშაობს:**
→ Environment Variables შემოწმება → Re-deploy

---

## 🎉 როცა მუშაობს

ყოველდღე 13:00-ზე ავტომატურად მიიღებ:
- 3 TikTok პოსტს (სურათი)
- Caption-ებს
- Hashtag-ებს
- A/B ტესტირებას

აფასებ → Bot სწავლობს → გაუმჯობესდება!

---

**დეტალები:** იხილე `README.md` 📖
