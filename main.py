import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
MAIN_MENU, COURSES, BAKERY_ORDER, PAYMENT, ORDER_DETAILS = range(5)

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("📚 Образовательные курсы", callback_data="courses")],
        [InlineKeyboardButton("🍰 Заказать в кондитерской", callback_data="bakery")],
        [InlineKeyboardButton("❓ Помощь", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Привет, {user.first_name}! 👋\n\n"
        "Я бот-консультант кондитерской Софико. Чем могу помочь?",
        reply_markup=reply_markup
    )
    return MAIN_MENU

# Help command handler
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = (
        "🤖 *Как пользоваться ботом:*\n\n"
        "*/start* - Начать взаимодействие с ботом\n"
        "*/courses* - Просмотр доступных образовательных курсов\n"
        "*/order* - Сделать заказ в кондитерской\n"
        "*/help* - Показать это сообщение\n\n"
        "Если у вас возникли вопросы, напишите нам: example@email.com"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

# Callback query handler
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle button presses."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "courses":
        return await show_courses(update, context)
    elif query.data == "bakery":
        return await bakery_order(update, context)
    elif query.data == "help":
        await query.edit_message_text(
            "🤖 *Как пользоваться ботом:*\n\n"
            "*/start* - Начать взаимодействие с ботом\n"
            "*/courses* - Просмотр доступных образовательных курсов\n"
            "*/order* - Сделать заказ в кондитерской\n"
            "*/help* - Показать это сообщение\n\n"
            "Если у вас возникли вопросы, напишите нам: example@email.com",
            parse_mode="Markdown"
        )
        return MAIN_MENU
    elif query.data.startswith("course_"):
        course_id = query.data.split("_")[1]
        return await course_details(update, context, course_id)
    elif query.data.startswith("pay_course_"):
        course_id = query.data.split("_")[2]
        return await process_payment(update, context, course_id)
    elif query.data.startswith("bakery_item_"):
        item_id = query.data.split("_")[2]
        return await add_to_order(update, context, item_id)
    elif query.data == "checkout":
        return await checkout(update, context)
    elif query.data == "back_to_main":
        keyboard = [
            [InlineKeyboardButton("📚 Образовательные курсы", callback_data="courses")],
            [InlineKeyboardButton("🍰 Заказать в кондитерской", callback_data="bakery")],
            [InlineKeyboardButton("❓ Помощь", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "Главное меню. Чем могу помочь?",
            reply_markup=reply_markup
        )
        return MAIN_MENU
    
    return MAIN_MENU

# Show available courses
async def show_courses(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show available courses."""
    # Sample courses data - in a real app, this would come from a database
    courses = [
        {"id": "1", "name": "Основы кондитерского искусства", "price": 5000},
        {"id": "2", "name": "Продвинутые техники декорирования", "price": 7500},
        {"id": "3", "name": "Шоколадное мастерство", "price": 6000}
    ]
    
    keyboard = []
    for course in courses:
        keyboard.append([InlineKeyboardButton(
            f"{course['name']} - {course['price']} руб.", 
            callback_data=f"course_{course['id']}"
        )])
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query = update.callback_query
    if query:
        await query.edit_message_text(
            "📚 *Доступные образовательные курсы:*\n"
            "Выберите курс для получения подробной информации:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "📚 *Доступные образовательные курсы:*\n"
            "Выберите курс для получения подробной информации:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    
    return COURSES

# Course details
async def course_details(update: Update, context: ContextTypes.DEFAULT_TYPE, course_id: str) -> int:
    """Show course details and payment options."""
    # Sample course details - in a real app, this would come from a database
    courses = {
        "1": {
            "name": "Основы кондитерского искусства",
            "description": "Базовый курс для начинающих кондитеров. Вы научитесь готовить основные виды теста, кремов и начинок.",
            "duration": "4 недели",
            "price": 5000
        },
        "2": {
            "name": "Продвинутые техники декорирования",
            "description": "Курс для тех, кто хочет освоить сложные техники украшения тортов и пирожных.",
            "duration": "6 недель",
            "price": 7500
        },
        "3": {
            "name": "Шоколадное мастерство",
            "description": "Специализированный курс по работе с шоколадом. Вы научитесь темперировать шоколад и создавать шоколадные фигуры.",
            "duration": "3 недели",
            "price": 6000
        }
    }
    
    course = courses.get(course_id)
    if not course:
        await update.callback_query.edit_message_text("Курс не найден. Пожалуйста, выберите другой курс.")
        return await show_courses(update, context)
    
    keyboard = [
        [InlineKeyboardButton("💳 Оплатить курс", callback_data=f"pay_course_{course_id}")],
        [InlineKeyboardButton("⬅️ Назад к курсам", callback_data="courses")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    course_text = (
        f"*{course['name']}*\n\n"
        f"{course['description']}\n\n"
        f"*Продолжительность:* {course['duration']}\n"
        f"*Стоимость:* {course['price']} руб."
    )
    
    await update.callback_query.edit_message_text(
        course_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    
    return COURSES

# Process payment for a course
async def process_payment(update: Update, context: ContextTypes.DEFAULT_TYPE, course_id: str) -> int:
    """Process payment for a course."""
    # Sample course details - in a real app, this would come from a database
    courses = {
        "1": {"name": "Основы кондитерского искусства", "price": 5000},
        "2": {"name": "Продвинутые техники декорирования", "price": 7500},
        "3": {"name": "Шоколадное мастерство", "price": 6000}
    }
    
    course = courses.get(course_id)
    if not course:
        await update.callback_query.edit_message_text("Курс не найден. Пожалуйста, выберите другой курс.")
        return await show_courses(update, context)
    
    # In a real app, you would integrate with a payment provider here
    # For this example, we'll just simulate a payment process
    
    keyboard = [
        [InlineKeyboardButton("💳 Оплатить через банковскую карту", callback_data=f"payment_card_{course_id}")],
        [InlineKeyboardButton("⬅️ Назад", callback_data=f"course_{course_id}")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        f"Оплата курса: *{course['name']}*\n\n"
        f"Сумма к оплате: *{course['price']} руб.*\n\n"
        "Выберите способ оплаты:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    
    # Schedule a payment reminder for 24 hours later
    job_context = {
        'chat_id': update.effective_chat.id,
        'user_id': update.effective_user.id,
        'course_name': course['name'],
        'course_price': course['price']
    }
    context.job_queue.run_once(payment_reminder, 86400, data=job_context, name=f"reminder_{update.effective_user.id}_{course_id}")
    
    return PAYMENT

# Payment reminder
async def payment_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a payment reminder."""
    job_data = context.job.data
    await context.bot.send_message(
        job_data['chat_id'],
        f"Напоминание: у вас есть незавершенная оплата курса *{job_data['course_name']}* "
        f"на сумму *{job_data['course_price']} руб.*\n\n"
        "Для завершения оплаты, пожалуйста, вернитесь в бот и выберите курс снова.",
        parse_mode="Markdown"
    )

# Bakery order
async def bakery_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show bakery items for ordering."""
    # Sample bakery items - in a real app, this would come from a database
    bakery_items = [
        {"id": "1", "name": "Торт 'Наполеон'", "price": 1500},
        {"id": "2", "name": "Эклеры (набор 6 шт.)", "price": 800},
        {"id": "3", "name": "Макаронс (набор 12 шт.)", "price": 1200},
        {"id": "4", "name": "Чизкейк", "price": 900}
    ]
    
    # Initialize order in user data if not exists
    if 'order' not in context.user_data:
        context.user_data['order'] = []
    
    keyboard = []
    for item in bakery_items:
        keyboard.append([InlineKeyboardButton(
            f"{item['name']} - {item['price']} руб.", 
            callback_data=f"bakery_item_{item['id']}"
        )])
    
    # Add checkout button if there are items in the order
    if context.user_data['order']:
        total = sum(item['price'] * item['quantity'] for item in context.user_data['order'])
        keyboard.append([InlineKeyboardButton(f"🛒 Оформить заказ ({total} руб.)", callback_data="checkout")])
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Show current order if exists
    order_text = ""
    if context.user_data['order']:
        order_text = "\n\n*Ваш текущий заказ:*\n"
        for item in context.user_data['order']:
            order_text += f"• {item['name']} x{item['quantity']} - {item['price'] * item['quantity']} руб.\n"
    
    query = update.callback_query
    if query:
        await query.edit_message_text(
            "🍰 *Меню кондитерской Софико:*\n"
            "Выберите товары для заказа:" + order_text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "🍰 *Меню кондитерской Софико:*\n"
            "Выберите товары для заказа:" + order_text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    
    return BAKERY_ORDER

# Add item to order
async def add_to_order(update: Update, context: ContextTypes.DEFAULT_TYPE, item_id: str) -> int:
    """Add an item to the order."""
    # Sample bakery items - in a real app, this would come from a database
    bakery_items = {
        "1": {"name": "Торт 'Наполеон'", "price": 1500},
        "2": {"name": "Эклеры (набор 6 шт.)", "price": 800},
        "3": {"name": "Макаронс (набор 12 шт.)", "price": 1200},
        "4": {"name": "Чизкейк", "price": 900}
    }
    
    item = bakery_items.get(item_id)
    if not item:
        await update.callback_query.edit_message_text("Товар не найден. Пожалуйста, выберите другой товар.")
        return await bakery_order(update, context)
    
    # Initialize order in user data if not exists
    if 'order' not in context.user_data:
        context.user_data['order'] = []
    
    # Check if item already in order
    for order_item in context.user_data['order']:
        if order_item['id'] == item_id:
            order_item['quantity'] += 1
            break
    else:
        # Add new item to order
        context.user_data['order'].append({
            'id': item_id,
            'name': item['name'],
            'price': item['price'],
            'quantity': 1
        })
    
    await update.callback_query.answer(f"{item['name']} добавлен в заказ!")
    
    # Return to bakery order menu
    return await bakery_order(update, context)

# Checkout process
async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process the checkout."""
    if not context.user_data.get('order'):
        await update.callback_query.edit_message_text("Ваш заказ пуст. Пожалуйста, добавьте товары в заказ.")
        return await bakery_order(update, context)
    
    # Calculate total
    total = sum(item['price'] * item['quantity'] for item in context.user_data['order'])
    
    # Format order details
    order_details = "*Детали заказа:*\n"
    for item in context.user_data['order']:
        order_details += f"• {item['name']} x{item['quantity']} - {item['price'] * item['quantity']} руб.\n"
    
    order_details += f"\n*Итого:* {total} руб."
    
    keyboard = [
        [InlineKeyboardButton("📱 Оставить контактные данные", callback_data="provide_contact")],
        [InlineKeyboardButton("⬅️ Вернуться к меню", callback_data="bakery")],
        [InlineKeyboardButton("❌ Отменить заказ", callback_data="cancel_order")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        f"🛒 *Оформление заказа*\n\n"
        f"{order_details}\n\n"
        "Для завершения заказа, пожалуйста, оставьте ваши контактные данные.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    
    return ORDER_DETAILS

# Main function
def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [
                CallbackQueryHandler(button),
                CommandHandler("courses", show_courses),
                CommandHandler("order", bakery_order)
            ],
            COURSES: [
                CallbackQueryHandler(button)
            ],
            BAKERY_ORDER: [
                CallbackQueryHandler(button)
            ],
            PAYMENT: [
                CallbackQueryHandler(button)
            ],
            ORDER_DETAILS: [
                CallbackQueryHandler(button)
            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )
    
    application.add_handler(conv_handler)
    
    # Add standalone command handlers
    application.add_handler(CommandHandler("help", help_command))
    
    # Start the Bot
    application.run_polling()

if __name__ == "__main__":
    main()