import telebot
import csv
from telebot import types
import config
import os

prSTforCSV = []

bot = telebot.TeleBot(config.TOKEN2)
prdsSt = dict()
tablename = '*Продукт, Калорийность, Белки, Жиры, Углеводы*'
prds = []

usr_carts = dict()
usersdate = dict()


def sumcen(id, dictp):
    s = dictp[id]
    col = 0
    bel = 0
    ji = 0
    ugl = 0
    print(s)
    for row in s:
        row = row.split(', ')

        col += round(float(row[len(row) - 5 + 1].replace(',', '.')[:-5]), 2)

        bel += round(float(row[len(row) - 5 + 2].replace(',', '.')[:-2]), 2)

        ji += round(float(row[len(row) - 5 + 3].replace(',', '.')[:-2]), 2)

        ugl += round(float(row[len(row) - 5 + 4].replace(',', '.')[:-2]), 2)

    return f'{round(col, 2)} кКал, {round(bel, 2)} г, {round(ji, 2)} г, {round(ugl, 2)} г'


def cart(dictp, id, cartproduct):  # Корзина
    # global usr_carts
    if dictp.get(id, False) is False:  # если в словаре нет такого ключа
        dictp[id] = [f'1) {cartproduct}']  # добавляем его и помещает туда список с одним значением
    else:  # если такой ключ уже есть
        dictp[id].append(f'{len(dictp[id]) + 1}) {cartproduct}')  # добавляем значение в конец списка


def findNUJ(mass, product):
    nujmass = []
    print(product)
    if len(product) == 1:
        print(product)
        nujmass = []
        for pr in mass:
            pr1 = pr[0].split()
            if product[0] == pr1[0].lower() or product[0] + "," == pr1[0].lower():
                nujmass.append(pr)
        return nujmass
    else:
        for pr in mass:
            pr1 = pr[0].split(', ')
            pr1 = ' '.join(pr1).lower()
            # print(pr1)
            c = 0
            for j in product:
                if j in pr1:
                    c += 1
            if c == len(product):
                nujmass.append(pr)
    return nujmass


def findproduct(product):
    directory = 'data'
    base = []
    productbase = []
    for filename in os.scandir(directory):
        if filename.is_file():
            filename = str(filename)[11:-2]
            base.append(filename)
    for i in range(len(base)):
        with open(f"data\{base[i]}", encoding='utf8') as csvfile:
            reader = csv.reader(csvfile)
            csvf = []
            for row in reader:
                if len(row) != 5:
                    continue
                csvf.append(row)
            for j in csvf:
                if product in j[0].lower():  # if product in j[0].lower()
                    productbase.append(j)
    return productbase


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет, чтобы появилась панель кнопок введите /buttons')


@bot.message_handler(commands=['buttons'])
def button_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Найти продукт")
    markup.add(item1)
    item2 = types.KeyboardButton("Корзина")
    markup.add(item2)

    bot.send_message(message.chat.id, 'Выберете в панели нужную вам услугу', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def any_msg(message):
    global usersdate
    user_id = message.from_user.id
    print(user_id)

    d = message.text.capitalize()
    print(d, type(d))

    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text="Выбрать из списка", callback_data="test")
    keyboard.add(callback_button)

    callback_button3 = types.InlineKeyboardButton(text="Добавить в корзину", callback_data="cart")
    keyboard.add(callback_button3)

    if d == "Корзина":

        cartkb = types.InlineKeyboardMarkup()
        callback_button = types.InlineKeyboardButton(text="Удалить корзину", callback_data="delete")
        cartkb.add(callback_button)

        if user_id not in usr_carts.keys():
            bot.send_message(message.chat.id, "Корзина пуста")
        else:
            s = sumcen(message.chat.id, usr_carts)
            bot.send_message(message.chat.id, tablename + '\n' + '\n'.join(
                map(str, usr_carts[message.chat.id])) + f'\n *Суммарная ценность*: \n {s}',
                             parse_mode='Markdown', reply_markup=cartkb)  # '\n'.join(map(str, prdsSt))

    elif d == "Найти продукт":
        bot.send_message(user_id, "Введите свой продукт")

    elif d.isdigit():
        global prdsSt

        keyboard2 = types.InlineKeyboardMarkup()
        callback_button4 = types.InlineKeyboardButton(text="Добавить в корзину", callback_data="add")
        keyboard2.add(callback_button4)

        bot.send_message(message.chat.id, f"{tablename}\n{prdsSt[user_id][int(d)][len(d) + 1:].lstrip()}",
                         parse_mode='Markdown', reply_markup=keyboard2)
        usersdate[user_id] = f"{prdsSt[user_id][int(d)][len(d) + 1:].lstrip()}"

    else:
        product = message.text.lower().split()
        global prSTforCSV
        prSTforCSV = []

        prds = findproduct(product[0])
        prds = findNUJ(prds, product)
        prSTforCSV = prds.copy()

        # global prdsSt
        prdsSt[message.chat.id] = []
        for prd in prds:
            prd = ", ".join(prd) + '\n'

            if prdsSt.get(message.chat.id, False) is False:  # если в словаре нет такого ключа
                prdsSt[message.chat.id] = [prd]  # добавляем его и помещает туда список с одним значением
            else:  # если такой ключ уже есть
                prdsSt[message.chat.id].append(prd)  # добавляем значение в конец списка

        if len(prdsSt[message.chat.id]) == 0:
            bot.send_message(message.chat.id, "Продукт не найден")
        else:
            user_id = message.chat.id

            r = "*Продукт, Калорийность, Белки, Жиры, Углеводы*"

            bot.send_message(message.chat.id, f"{r}\n{prdsSt[message.chat.id][0]}", reply_markup=keyboard,
                             parse_mode='Markdown')
            usersdate[user_id] = prdsSt[message.chat.id][0]


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        global prdsSt
        global tablename
        global prSTforCSV
        global usr_carts
        if call.data == "test":
            if len(prdsSt[call.message.chat.id]) > 25:
                prdsSt[call.message.chat.id] = prdsSt[call.message.chat.id][:25]
            for i in range(len(prdsSt[call.message.chat.id])):
                prdsSt[call.message.chat.id][i] = f'{i + 1})  ' + prdsSt[call.message.chat.id][i]
            prdsSt[call.message.chat.id].insert(0, tablename)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="*Выберите* нужный вам товар из списка. *цифрой*", parse_mode='Markdown')

            bot.send_message(call.message.chat.id, '\n'.join(map(str, prdsSt[call.message.chat.id])),
                             parse_mode='Markdown')

        elif call.data == "delete":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=f"Корзина очищена", parse_mode='Markdown')
            usr_carts.pop(call.message.chat.id)

        elif call.data == "cart" or 'add':
            user_id = call.message.chat.id
            cart(usr_carts, user_id, usersdate[user_id])
            print(usr_carts)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=f"*Продукт* {usersdate[user_id]} *добавлен в корзину*", parse_mode='Markdown')


bot.infinity_polling()
