"""
Telegram Bot - Main interface for TikTok Parenting Agent
With Health Check Web Server for Render deployment
"""
import os
import json
from datetime import datetime
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiohttp import web
import asyncio

import config
from content_creator import ContentCreator
from design_generator import DesignGenerator
from news_tracker import NewsTracker

class ParentingBot:
    def __init__(self):
        self.content_creator = ContentCreator()
        self.design_generator = DesignGenerator()
        self.news_tracker = NewsTracker()
        self.current_variants = {}
        self.scheduler = None
        self.load_stats()
    
    def load_stats(self):
        """Load bot statistics"""
        try:
            with open(config.STATS_FILE, 'r', encoding='utf-8') as f:
                self.stats = json.load(f)
        except:
            self.stats = {
                'start_date': datetime.now().isoformat(),
                'total_generated': 0,
                'total_feedback': 0,
                'by_format': {},
                'by_rating': {}
            }
    
    def save_stats(self):
        """Save bot statistics"""
        os.makedirs(config.DATA_DIR, exist_ok=True)
        with open(config.STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = f"""
🤖 გამარჯობა! მე ვარ Nika Parenting Bot

ვეხმარები შენ ყოველდღიურად TikTok კონტენტის შექმნაში მშობლობის თემაზე.

📅 ყოველდღე {config.GENERATION_HOUR}:00 საათზე:
• დაგენერირდება {config.get_variants_count()} ვარიანტი
• შეგიძლია აირჩიო საუკეთესო
• შეაფასო და გავაუმჯობესო

💡 ბრძანებები:
/generate - ახალი კონტენტის გენერაცია
/stats - სტატისტიკა
/help - დახმარება

{config.BRANDING}
        """
        
        # Save admin chat ID if not set
        if not config.ADMIN_CHAT_ID:
            chat_id = update.effective_chat.id
            print(f"\n🔑 Admin Chat ID: {chat_id}")
            print(f"დაამატე ეს .env ფაილში: ADMIN_CHAT_ID={chat_id}\n")
        
        await update.message.reply_text(welcome_message)
    
    async def generate_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /generate command"""
        await update.message.reply_text("⏳ ვგენერირებ კონტენტს... გთხოვ დაელოდე 30-60 წამს...")
        
        try:
            await self._generate_and_send(update.effective_chat.id, context)
        except Exception as e:
            await update.message.reply_text(f"❌ შეცდომა: {str(e)}\nსცადე თავიდან /generate")
    
    async def scheduled_generation(self, context: ContextTypes.DEFAULT_TYPE):
        """Scheduled daily content generation"""
        if not config.ADMIN_CHAT_ID:
            print("❌ ADMIN_CHAT_ID არ არის დაყენებული!")
            return
        
        chat_id = int(config.ADMIN_CHAT_ID)
        
        # Send greeting
        greeting = "🌅 დილა მშვიდობისა! ვგენერირებ დღევანდელ კონტენტს..."
        await context.bot.send_message(chat_id=chat_id, text=greeting)
        
        try:
            await self._generate_and_send(chat_id, context)
        except Exception as e:
            await context.bot.send_message(
                chat_id=chat_id, 
                text=f"❌ შეცდომა გენერაციისას: {str(e)}"
            )
    
    async def _generate_and_send(self, chat_id, context):
        """Generate content and send to user"""
        # Check if we should include news
        news_context = None
        if self.news_tracker.should_check_news_today():
            news_list = self.news_tracker.check_news()
            if news_list:
                news_context = self.news_tracker.format_news_context(news_list)
        
        # Generate content
        variants_count = config.get_variants_count()
        variants = self.content_creator.generate_content_ideas(
            count=variants_count,
            news_context=news_context
        )
        
        if not variants:
            await context.bot.send_message(
                chat_id=chat_id,
                text="❌ ვერ მოხერხდა კონტენტის გენერაცია. სცადე თავიდან."
            )
            return
        
        # Generate images and send
        session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.current_variants[chat_id] = {}
        
        header = f"""
📅 {datetime.now().strftime('%d.%m.%Y')} | დღევანდელი კონტენტი
━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        await context.bot.send_message(chat_id=chat_id, text=header)
        
        for idx, variant in enumerate(variants, 1):
            try:
                # Generate image
                img = self.design_generator.generate_image(variant)
                
                filename = f"{session_id}_variant_{idx}.png"
                filepath = self.design_generator.save_image(img, filename)
                
                # Prepare caption
                caption = self._format_variant_caption(variant, idx)
                
                # Create keyboard
                keyboard = self._create_variant_keyboard(idx)
                
                # Send photo
                with open(filepath, 'rb') as photo:
                    await context.bot.send_photo(
                        chat_id=chat_id,
                        photo=photo,
                        caption=caption,
                        reply_markup=keyboard,
                        parse_mode='HTML'
                    )
                
                # Store variant for later reference
                self.current_variants[chat_id][idx] = {
                    'content': variant,
                    'filepath': filepath,
                    'session_id': session_id
                }
                
                # Update stats
                self.stats['total_generated'] += 1
                format_type = variant.get('format', 'unknown')
                self.stats['by_format'][format_type] = \
                    self.stats['by_format'].get(format_type, 0) + 1
                
            except Exception as e:
                print(f"Error generating variant {idx}: {e}")
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"❌ ვარიანტი {idx} - შეცდომა გენერაციისას"
                )
        
        self.save_stats()
        
        footer = """
━━━━━━━━━━━━━━━━━━━━━━━━━━
რომელი მოგწონს? შეაფასე ღილაკებით! 
        """
        await context.bot.send_message(chat_id=chat_id, text=footer)
    
    def _format_variant_caption(self, variant, idx):
        """Format caption for variant"""
        format_names = {
            'myth_vs_reality': '💭 მითი VS რეალობა',
            'self_assessment': '🤔 თვით-შეფასება',
            'practical_scenario': '📋 პრაქტიკული სცენარი',
            'quick_tip': '💡 სწრაფი რჩევა',
            'mini_story': '📖 მინი ისტორია'
        }
        
        format_name = format_names.get(variant.get('format'), 'კონტენტი')
        
        caption = f"""
<b>📱 ვარიანტი {idx}</b> | {format_name}

<b>Caption TikTok-ისთვის:</b>
{variant.get('caption', '')}

<b>Hashtags:</b>
{' '.join(variant.get('hashtags', config.DEFAULT_HASHTAGS))}
        """
        
        return caption.strip()
    
    def _create_variant_keyboard(self, variant_idx):
        """Create inline keyboard for variant"""
        keyboard = [
            [
                InlineKeyboardButton("❤️", callback_data=f"rate_{variant_idx}_love"),
                InlineKeyboardButton("👍", callback_data=f"rate_{variant_idx}_like"),
                InlineKeyboardButton("😐", callback_data=f"rate_{variant_idx}_ok"),
                InlineKeyboardButton("👎", callback_data=f"rate_{variant_idx}_dislike"),
            ],
            [
                InlineKeyboardButton("🔄 თავიდან", callback_data=f"regen_{variant_idx}"),
                InlineKeyboardButton("✏️ რედაქტირება", callback_data=f"edit_{variant_idx}"),
            ],
            [
                InlineKeyboardButton("🎨 სტილის შეცვლა", callback_data=f"style_{variant_idx}"),
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        chat_id = update.effective_chat.id
        
        if data.startswith('rate_'):
            await self._handle_rating(query, data, chat_id)
        elif data.startswith('regen_'):
            await self._handle_regenerate(query, data, chat_id, context)
        elif data.startswith('edit_'):
            await self._handle_edit_request(query, data, chat_id)
        elif data.startswith('style_'):
            await self._handle_style_change(query, data, chat_id, context)
    
    async def _handle_rating(self, query, data, chat_id):
        """Handle rating feedback"""
        parts = data.split('_')
        variant_idx = int(parts[1])
        rating = parts[2]
        
        rating_emoji = {
            'love': '❤️',
            'like': '👍',
            'ok': '😐',
            'dislike': '👎'
        }
        
        # Get variant
        if chat_id in self.current_variants and variant_idx in self.current_variants[chat_id]:
            variant = self.current_variants[chat_id][variant_idx]['content']
            
            # Record feedback
            self.content_creator.record_feedback(variant, rating_emoji[rating])
            
            # Update stats
            self.stats['total_feedback'] += 1
            self.stats['by_rating'][rating] = self.stats['by_rating'].get(rating, 0) + 1
            self.save_stats()
            
            await query.edit_message_reply_markup(reply_markup=None)
            await query.message.reply_text(
                f"✅ შეფასება მიღებულია: {rating_emoji[rating]}\n"
                f"გმადლობთ! ეს დამეხმარება გავაუმჯობესო შემდეგი გენერაციები."
            )
        else:
            await query.message.reply_text("❌ ვარიანტი ვერ მოიძებნა. სცადე ახალი გენერაცია /generate")
    
    async def _handle_regenerate(self, query, data, chat_id, context):
        """Handle regeneration request"""
        variant_idx = int(data.split('_')[1])
        
        await query.message.reply_text("⏳ ვქმნი ახალ ვერსიას...")
        
        if chat_id in self.current_variants and variant_idx in self.current_variants[chat_id]:
            # Generate new version
            new_content = self.content_creator.generate_content_ideas(count=1)[0]
            
            # Generate image
            img = self.design_generator.generate_image(new_content)
            session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{session_id}_regen_{variant_idx}.png"
            filepath = self.design_generator.save_image(img, filename)
            
            # Send
            caption = self._format_variant_caption(new_content, variant_idx)
            keyboard = self._create_variant_keyboard(variant_idx)
            
            with open(filepath, 'rb') as photo:
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=photo,
                    caption=f"🔄 ახალი ვერსია:\n\n{caption}",
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
            
            # Update stored variant
            self.current_variants[chat_id][variant_idx] = {
                'content': new_content,
                'filepath': filepath,
                'session_id': session_id
            }
    
    async def _handle_edit_request(self, query, data, chat_id):
        """Handle edit request"""
        variant_idx = int(data.split('_')[1])
        
        await query.message.reply_text(
            f"✏️ რედაქტირება ვარიანტი {variant_idx}:\n\n"
            "დაწერე როგორ უნდა შევცვალო:\n"
            "მაგ: 'უფრო მარტივი ენით' ან 'დაამატე კონკრეტული მაგალითი'\n\n"
            f"პასუხში დაწერე: edit{variant_idx} შენი კომენტარი"
        )
    
    async def _handle_style_change(self, query, data, chat_id, context):
        """Handle visual style change"""
        variant_idx = int(data.split('_')[1])
        
        if chat_id not in self.current_variants or variant_idx not in self.current_variants[chat_id]:
            await query.message.reply_text("❌ ვარიანტი ვერ მოიძებნა")
            return
        
        variant = self.current_variants[chat_id][variant_idx]
        content = variant['content']
        
        # Get different style
        current_styles = list(config.VISUAL_STYLE_DISTRIBUTION.keys())
        new_style = current_styles[0]
        
        await query.message.reply_text(f"🎨 ვცვლი სტილს... ახალი: {new_style}")
        
        # Generate with new style
        img = self.design_generator.generate_image(content, style=new_style)
        session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{session_id}_style_{variant_idx}.png"
        filepath = self.design_generator.save_image(img, filename)
        
        caption = self._format_variant_caption(content, variant_idx)
        keyboard = self._create_variant_keyboard(variant_idx)
        
        with open(filepath, 'rb') as photo:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=f"🎨 ახალი სტილი ({new_style}):\n\n{caption}",
                reply_markup=keyboard,
                parse_mode='HTML'
            )
        
        variant['filepath'] = filepath
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages for editing"""
        text = update.message.text
        chat_id = update.effective_chat.id
        
        # Check if it's an edit command
        if text.startswith('edit'):
            parts = text.split(' ', 1)
            if len(parts) == 2:
                variant_num = parts[0].replace('edit', '')
                try:
                    variant_idx = int(variant_num)
                    feedback_text = parts[1]
                    
                    if chat_id in self.current_variants and variant_idx in self.current_variants[chat_id]:
                        await update.message.reply_text("⏳ ვამუშავებ შენს კომენტარებს...")
                        
                        original = self.current_variants[chat_id][variant_idx]['content']
                        
                        # Regenerate with feedback
                        new_content = self.content_creator.regenerate_with_feedback(
                            original, feedback_text
                        )
                        
                        # Save this edit for learning
                        self.content_creator.add_custom_edit(feedback_text)
                        
                        # Generate new image
                        img = self.design_generator.generate_image(new_content)
                        session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
                        filename = f"{session_id}_edited_{variant_idx}.png"
                        filepath = self.design_generator.save_image(img, filename)
                        
                        caption = self._format_variant_caption(new_content, variant_idx)
                        keyboard = self._create_variant_keyboard(variant_idx)
                        
                        with open(filepath, 'rb') as photo:
                            await context.bot.send_photo(
                                chat_id=chat_id,
                                photo=photo,
                                caption=f"✏️ რედაქტირებული ვერსია:\n\n{caption}",
                                reply_markup=keyboard,
                                parse_mode='HTML'
                            )
                        
                        self.current_variants[chat_id][variant_idx] = {
                            'content': new_content,
                            'filepath': filepath,
                            'session_id': session_id
                        }
                    else:
                        await update.message.reply_text("❌ ვარიანტი ვერ მოიძებნა")
                except:
                    pass
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show statistics"""
        start_date = datetime.fromisoformat(self.stats['start_date'])
        days_running = (datetime.now() - start_date).days
        
        is_learning = config.is_learning_phase()
        phase = "სასწავლო ფაზა" if is_learning else "ნორმალური რეჟიმი"
        
        stats_text = f"""
📊 სტატისტიკა

🗓 მუშაობს: {days_running} დღე
📍 რეჟიმი: {phase}
📝 გენერირებული: {self.stats['total_generated']}
💬 შეფასებები: {self.stats['total_feedback']}

📈 ფორმატების სტატისტიკა:
        """
        
        for format_type, count in self.stats.get('by_format', {}).items():
            stats_text += f"\n  • {format_type}: {count}"
        
        stats_text += "\n\n⭐ შეფასებები:"
        for rating, count in self.stats.get('by_rating', {}).items():
            stats_text += f"\n  • {rating}: {count}"
        
        await update.message.reply_text(stats_text)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help"""
        help_text = """
📖 დახმარება

🔧 ბრძანებები:
/generate - ახალი კონტენტის გენერაცია
/stats - სტატისტიკა
/help - ეს დახმარება

💡 როგორ გამოვიყენო:

1️⃣ ყოველ დღე 13:00-ზე ავტომატურად მიიღებ 3 ვარიანტს
2️⃣ შეაფასე თითოეული: ❤️👍😐👎
3️⃣ გამოიყენე ღილაკები:
   🔄 თავიდან - ახალი გენერაცია
   ✏️ რედაქტირება - შენი კომენტარებით
   🎨 სტილის შეცვლა - სხვა დიზაინი

4️⃣ ჩამოტვირთე და ატვირთე TikTok-ზე!

💬 რედაქტირებისთვის:
დაწერე: edit1 შენი კომენტარი
მაგ: "edit1 უფრო მარტივი ენით"

🎯 რაც მეტს აფასებ, მით უკეთესი ხდება!
        """
        await update.message.reply_text(help_text)
    
    async def post_init(self, application: Application):
        """Initialize scheduler after application is fully started"""
        # Setup scheduler AFTER event loop is running
        self.scheduler = AsyncIOScheduler(timezone=pytz.timezone(config.TIMEZONE))
        self.scheduler.add_job(
            self.scheduled_generation,
            'cron',
            hour=config.GENERATION_HOUR,
            minute=config.GENERATION_MINUTE,
            args=[application]
        )
        self.scheduler.start()
        print(f"⏰ Scheduler started - Daily generation at {config.GENERATION_HOUR}:{config.GENERATION_MINUTE:02d}")
    
    async def health_check(self, request):
        """Health check endpoint for Render"""
        return web.Response(text="OK", status=200)
    
    async def start_web_server(self):
        """Start simple web server for health checks"""
        app = web.Application()
        app.router.add_get('/', self.health_check)
        app.router.add_get('/health', self.health_check)
        
        port = int(os.environ.get('PORT', 10000))
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', port)
        await site.start()
        print(f"🌐 Health check server started on port {port}")
    
    def run(self):
        """Run the bot"""
        # Create application
        application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("generate", self.generate_command))
        application.add_handler(CommandHandler("stats", self.stats_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CallbackQueryHandler(self.button_callback))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))
        
        # Register post_init to start scheduler after event loop is ready
        application.post_init = self.post_init
        
        # Start health check web server
        asyncio.get_event_loop().create_task(self.start_web_server())
        
        # Run bot
        print("🤖 Bot started!")
        print(f"📍 Timezone: {config.TIMEZONE}")
        
        application.run_polling()

if __name__ == '__main__':
    bot = ParentingBot()
    bot.run()
