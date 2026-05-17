import sqlite3
import telebot
from telebot import types
from datetime import datetime
TOKEN = "8269545478:AAGB38IvD4osgsqqW2djKfb_LeP3Xfq5x8U"


bot = telebot.TeleBot(TOKEN)

conn = sqlite3.connect("flowers.db", check_same_thread=False)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS flowers (
    name TEXT,
    count INTEGER
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS history (
    action TEXT,
    flower TEXT,
    count INTEGER,
    date TEXT
)
""")

conn.commit()

conn.commit()
flowers = {}

@bot.message_handler(commands=['start'])
def start(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn1 = types.KeyboardButton("🌸 Добавить цветок")
    btn2 = types.KeyboardButton("📦 Остатки")
    btn3 = types.KeyboardButton("➕ Приход")
    btn4 = types.KeyboardButton("➖ Списание")
    btn5 = types.KeyboardButton("🗑 Удалить цветок")
    btn6 = types.KeyboardButton("🔍 Поиск")
    btn7 = types.KeyboardButton("📜 История")
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn5, btn6)
    markup.add(btn7)


    bot.send_message(
        message.chat.id,
        "🌸 Система учёта цветов",
        reply_markup=markup
    )
temp_data = {}

@bot.message_handler(func=lambda message: message.text == "🌸 Добавить цветок")
def add_flower_start(message):

    bot.send_message(
        message.chat.id,
        "Введите название цветка 🌸"
    )

    bot.register_next_step_handler(message, get_flower_name)
def get_flower_name(message):
    buttons = [
     "🌸 Добавить цветок",
     "📦 Остатки",
     "➕ Приход",
     "➖ Списание",
     "🗑 Удалить цветок"
    ]

    if message.text in buttons:

     bot.send_message(
        message.chat.id,
        "Сначала завершите текущее действие ❌"
     )

     return

    temp_data[message.chat.id] = {}

    temp_data[message.chat.id]["flower"] = message.text

    bot.send_message(
        message.chat.id,
        "Введите количество 📦"
    )

    bot.register_next_step_handler(message, get_flower_count)
def get_flower_count(message):

    count = message.text

    if not count.isdigit():

        bot.send_message(
            message.chat.id,
            "Введите только цифры ❌"
        )

        bot.register_next_step_handler(message, get_flower_count)

        return

    flower = temp_data[message.chat.id]["flower"]

    cursor.execute(
     "INSERT INTO flowers VALUES (?, ?)",
     (flower, int(count))
     )

    conn.commit()
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    cursor.execute(
     "INSERT INTO history VALUES (?, ?, ?, ?)",
     ("add", flower, count, date)
    )   
    conn.commit()
    bot.send_message(
        message.chat.id,
        f"🌸 {flower} добавлен\n📦 Количество: {count}"
    )    
@bot.message_handler(func=lambda message: message.text == "📦 Остатки")
@bot.message_handler(func=lambda message: message.text == "📦 Остатки")
@bot.message_handler(func=lambda message: message.text == "📦 Остатки")
def show_flowers(message):

    cursor.execute("SELECT * FROM flowers")

    data = cursor.fetchall()

    if not data:

        bot.send_message(
            message.chat.id,
            "Склад пуст 📦"
        )

        return

    markup = types.InlineKeyboardMarkup()

    for flower in data:

        btn = types.InlineKeyboardButton(
            text=f"🌸 {flower[0]}",
            callback_data=flower[0]
        )

        markup.add(btn)

    bot.send_message(
        message.chat.id,
        "Выберите цветок 🌸",
        reply_markup=markup
    )
@bot.message_handler(func=lambda message: message.text == "➕ Приход")
@bot.message_handler(func=lambda message: message.text == "➕ Приход")
def income_start(message):

    cursor.execute("SELECT * FROM flowers")

    data = cursor.fetchall()

    if not data:

        bot.send_message(
            message.chat.id,
            "Склад пуст 📦"
        )

        return

    markup = types.InlineKeyboardMarkup()

    for flower in data:

        btn = types.InlineKeyboardButton(
            text=f"🌸 {flower[0]}",
            callback_data=f"income_{flower[0]}"
        )

        markup.add(btn)

    bot.send_message(
        message.chat.id,
        "Выберите цветок для прихода ➕",
        reply_markup=markup
    )
def income_flower(message):

    flower = message.text
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute(
      "SELECT * FROM flowers WHERE name = ?",
      (flower,)
      )

    data = cursor.fetchone()

    if not data:

     bot.send_message(
        message.chat.id,
        "Такого цветка нет ❌"
     )

     return
    temp_data[message.chat.id] = {}

    temp_data[message.chat.id]["flower"] = flower

    bot.send_message(
        message.chat.id,
        "Введите количество ➕"
    )

    bot.register_next_step_handler(message, income_count)       
def income_count(message):

    count = message.text

    if not count.isdigit():

        bot.send_message(
            message.chat.id,
            "Введите только цифры ❌"
        )

        bot.register_next_step_handler(message, income_count)

        return

    flower = temp_data[message.chat.id]["flower"]

    cursor.execute(
     "UPDATE flowers SET count = count + ? WHERE name = ?",
     (int(count), flower)
     )

    conn.commit()
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute(
     "INSERT INTO history VALUES (?, ?, ?, ?)",
     ("income", flower, count, date)
      ) 

    conn.commit()
    bot.send_message(
     message.chat.id,
     f"➕ Добавлено {count}\n🌸 {flower} обновлён"
     )  
@bot.message_handler(func=lambda message: message.text == "➖ Списание")
@bot.message_handler(func=lambda message: message.text == "➖ Списание")
def remove_start(message):

    cursor.execute("SELECT * FROM flowers")

    data = cursor.fetchall()

    if not data:

        bot.send_message(
            message.chat.id,
            "Склад пуст 📦"
        )

        return

    markup = types.InlineKeyboardMarkup()

    for flower in data:

        btn = types.InlineKeyboardButton(
            text=f"🌸 {flower[0]}",
            callback_data=f"remove_{flower[0]}"
        )

        markup.add(btn)
    

    conn.commit()
    bot.send_message(
        message.chat.id,
        "Выберите цветок для списания ➖",
        reply_markup=markup
    )   
def remove_flower(message):

    flower = message.text

    cursor.execute(
    "SELECT * FROM flowers WHERE name = ?",
    (flower,)
    )

    data = cursor.fetchone()

    if not data:

     bot.send_message(
        message.chat.id,
        "Такого цветка нет ❌"
     )

     return
    temp_data[message.chat.id] = {}

    temp_data[message.chat.id]["flower"] = flower

    bot.send_message(
        message.chat.id,
        "Введите количество ➖"
    )

    bot.register_next_step_handler(message, remove_count)
def remove_count(message):
    count = message.text
    if not count.isdigit():

     bot.send_message(
        message.chat.id,
        "Введите только цифры ❌"
     )

     bot.register_next_step_handler(message, remove_count)

     return

    count = int(count)
    flower = temp_data[message.chat.id]["flower"]
    cursor.execute(
     "SELECT count FROM flowers WHERE name = ?",
     (flower,)
     )

    data = cursor.fetchone()

    current_count = data[0]

    if count > current_count:

     bot.send_message(
        message.chat.id,
        "Недостаточно цветов на складе ❌"
     )

     return

    cursor.execute(
      " UPDATE flowers SET count = count - ? WHERE name = ?",
      (count, flower)
     )

    conn.commit()
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute(
     "INSERT INTO history VALUES (?, ?, ?, ?)",
     ("remove", flower, count, date)
     )

    conn.commit()
    bot.send_message(
     message.chat.id,
     f"➖ Списано {count}\n🌸 {flower} обновлён"
     )
@bot.message_handler(func=lambda message: message.text == "🗑 Удалить цветок")
def delete_flower_start(message):

    bot.send_message(
        message.chat.id,
        "Введите название цветка для удаления 🗑"
    )

    bot.register_next_step_handler(message, delete_flower)
def delete_flower(message):

    flower = message.text

    cursor.execute(
        "SELECT * FROM flowers WHERE name = ?",
        (flower,)
    )

    data = cursor.fetchone()

    if not data:

        bot.send_message(
            message.chat.id,
            "Такого цветка нет ❌"
        )

        return

    cursor.execute(
        "DELETE FROM flowers WHERE name = ?",
        (flower,)
    )

    conn.commit()
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute(
     "INSERT INTO history VALUES (?, ?, ?, ?)",
     ("delete", flower, 0, date)
     )

    conn.commit()
    bot.send_message(
        message.chat.id,
        f"🗑 {flower} удалён"
    )
@bot.callback_query_handler(func=lambda call: True)

def callback_inline(call):

    # СПИСАНИЕ

    if call.data.startswith("remove_"):

        flower = call.data.replace("remove_", "")

        temp_data[call.message.chat.id] = {}

        temp_data[call.message.chat.id]["flower"] = flower

        bot.send_message(
            call.message.chat.id,
            f"🌸 {flower}\nВведите количество для списания ➖"
        )

        bot.register_next_step_handler_by_chat_id(
         call.message.chat.id,
         remove_count
         )

        return

    # ПРИХОД

    if call.data.startswith("income_"):

        flower = call.data.replace("income_", "")

        temp_data[call.message.chat.id] = {}

        temp_data[call.message.chat.id]["flower"] = flower

        bot.send_message(
            call.message.chat.id,
            f"🌸 {flower}\nВведите количество для прихода ➕"
        )

        bot.register_next_step_handler_by_chat_id(
         call.message.chat.id,
         income_count
         )

        return

    # ОСТАТКИ

    flower = call.data

    cursor.execute(
        "SELECT count FROM flowers WHERE name = ?",
        (flower,)
    )

    data = cursor.fetchone()

    if not data:

        bot.send_message(
            call.message.chat.id,
            "Цветок не найден ❌"
        )

        return

    count = data[0]

    bot.send_message(
        call.message.chat.id,
        f"🌸 {flower}\n📦 Остаток: {count}"
    )
@bot.message_handler(func=lambda message: message.text == "🔍 Поиск")
def search_start(message):

    bot.send_message(
        message.chat.id,
        "Введите название цветка 🔍"
    )

    bot.register_next_step_handler(
        message,
        search_flower
    )
def search_flower(message):

    flower = message.text

    cursor.execute(
        "SELECT count FROM flowers WHERE name = ?",
        (flower,)
    )

    data = cursor.fetchone()

    if not data:

        bot.send_message(
            message.chat.id,
            "Цветок не найден ❌"
        )

        return

    count = data[0]

    bot.send_message(
        message.chat.id,
        f"🌸 {flower}\n📦 Остаток: {count}"
    )
@bot.message_handler(func=lambda message: message.text == "📜 История")
def show_history(message):

    cursor.execute(
        "SELECT * FROM history"
    )

    data = cursor.fetchall()

    if not data:

        bot.send_message(
            message.chat.id,
            "История пуста 📜"
        )

        return

    result = "📜 История операций:\n\n"

    for item in data:

        action = item[0]
        flower = item[1]
        count = item[2]
        date = item[3]

        if action == "income":
            action_text = "➕ Приход"

        elif action == "remove":
            action_text = "➖ Списание"
        elif action == "add":
         action_text = "🌸 Добавление"
        elif action == "delete":
            action_text = "🗑 Удаление"

        else:
            action_text = action

        result += (
            f"{action_text}\n"
            f"🌸 {flower}\n"
            f"📦 {count}\n"
            f"🕒 {date}\n"f"{'-'*20}\n"
        )

    bot.send_message(
        message.chat.id,
        result
    )
print("FLOWER BOT STARTED 🌸")


bot.infinity_polling()