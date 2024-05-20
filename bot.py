import re
from pathlib import Path

import paramiko
import os

from dotenv import load_dotenv

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

import logging

import psycopg2
from psycopg2 import Error

load_dotenv()
TOKEN = os.getenv('TOKEN')


# Подключаем логирование
logging.basicConfig(
        filename='db_telegram.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO,
        encoding="utf-8"
)

logger = logging.getLogger(__name__)



def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')


def helpCommand(update: Update, context):
    update.message.reply_text('Help!')


def find_email_command(update: Update, context):
    update.message.reply_text('Введите текст для поиска email-адресов: ')

    return 'find_email'


def find_email(update: Update, context):
    user_input = update.message.text  # Получаем текст, содержащий(или нет) email-адреса

    emailRegex = re.compile(r'\b[a-zA-Z0-9.!#$%&\'*+/=?^_`{|}~-]+(?:\.[a-zA-Z0-9.!#$%&\'*+/=?^_`{|}~-]+)*' \
                r'@(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b')  # формат email-адреса

    emailList = emailRegex.findall(user_input)  # Ищем email-адреса

    if not emailList:  # Обрабатываем случай, когда email-адресов нет
        update.message.reply_text('Email-адреса не найдены')
        return ConversationHandler.END # Завершаем выполнение функции

    unique_emails = list(set(emailList))  # Remove duplicates
    emails = ''  # Создаем строку, в которую будем записывать email-адреса
    for i,email in enumerate(unique_emails):
        emails += f'{i+1}. {email}\n'

    update.message.reply_text(emails)  # Отправляем сообщение пользователю

    #сохраняем каждый email отдельно, чтобы потом их нормально залить в бд
    context.user_data['emails'] = unique_emails

    update.message.reply_text('Сохранить найденные email-адреса в базе данных? Отвечайте "Да" или "Нет": ')

    return 'save_emails'


def save_emails(update: Update, context):
    user_input = update.message.text
    if user_input == "Да" or user_input == "да":
        connection = connect_to_db()
        if connection:
            try:
                cursor = connection.cursor()
                emails = context.user_data.get('emails', [])
                for email in emails:
                    cursor.execute("INSERT INTO emails (email) VALUES (%s);", (email,))
                connection.commit()
                context.user_data.clear()
                update.message.reply_text('Email-адреса сохранены в базе данных!')
            except (Exception, Error) as error:
                logging.error(f"Произошла ошибка при сохранении email-адресов: {error}")
                update.message.reply_text(f'Произошла ошибка при сохранении email-адресов!{error}')
            finally:
                cursor.close()
                connection.close()
                logging.info("Соединение с PostgreSQL закрыто")
        else:
            update.message.reply_text('Не удалось подключиться к базе данных!')
    else:
        update.message.reply_text('Email-адреса не были сохранены в базе данных!')
    return ConversationHandler.END


def find_phone_number_command(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')

    return 'find_phone_number'


def find_phone_number(update: Update, context):
    user_input = update.message.text  # Получаем текст, содержащий(или нет) номера телефонов

    phoneNumRegex = re.compile(r'(?:\+?7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}')
    #^(?:\+?7|8)\s?\(?\d{3}\)?\s?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$
    #8 \(\d{3}\) \d{3}-\d{2}-\d{2}

    phoneNumberList = phoneNumRegex.findall(user_input)  # Ищем номера телефонов

    if not phoneNumberList:  # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END # Завершаем выполнение функции

    unique_phone_numbers = list(set(phoneNumberList))  # Remove duplicates
    phone_numbers = ''
    for i, number in enumerate(unique_phone_numbers):
        phone_numbers += f'{i+1}. {number}\n'

    update.message.reply_text(phone_numbers)

    # Save unique phone numbers
    context.user_data['phones'] = unique_phone_numbers

    update.message.reply_text('Сохранить найденные телефоны в базе данных? Отвечайте "Да" или "Нет": ')

    return 'save_phone_numbers'


def save_phone_numbers(update: Update, context):
    user_input = update.message.text
    if user_input == "Да" or user_input == "да":
        connection = connect_to_db()
        if connection:
            try:
                cursor = connection.cursor()
                phones = context.user_data.get('phones', [])
                for phone in phones:
                    cursor.execute("INSERT INTO phones (phone) VALUES (%s);", (phone,))
                connection.commit()
                context.user_data.clear()
                update.message.reply_text('Телефоны сохранены в базе данных!')
            except (Exception, Error) as error:
                logging.error(f"Произошла ошибка при сохранении телефонов: {error}")
                update.message.reply_text('Произошла ошибка при сохранении телефонов!')
            finally:
                cursor.close()
                connection.close()
                logging.info("Соединение с PostgreSQL закрыто")
        else:
            update.message.reply_text('Не удалось подключиться к базе данных!')
    else:
        update.message.reply_text('Телефоны не были сохранены в базе данных!')
    return ConversationHandler.END


def verify_password_command(update: Update, context):
    update.message.reply_text('Введите пароль для проверки: ')

    return 'verify_password'


def verify_password(update: Update, context):
    user_input = update.message.text #получаем текст

    passwordRegex = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()]).{8,}$')
    if passwordRegex.match(user_input):
        answer = 'Пароль сложный'
    else:
        answer = 'Пароль простой'
    update.message.reply_text(answer)  # Отправляем сообщение пользователю
    return ConversationHandler.END  # Завершаем работу обработчика диалога


def get_ssh_and_run_cmd(cmd):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command(cmd)
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    return data


def get_release(update: Update,context):
    update.message.reply_text('Результат работы: ')
    answer = get_ssh_and_run_cmd('lsb_release -a')
    update.message.reply_text(answer)
    return ConversationHandler.END  # Завершаем работу обработчика диалога


def get_uname(update: Update,context):
    update.message.reply_text('Об архитектуры процессора, имени хоста системы и версии ядра: ')
    answer = get_ssh_and_run_cmd('uname -a')
    update.message.reply_text(answer)
    return ConversationHandler.END  # Завершаем работу обработчика диалога


def get_uptime(update: Update,context):
    update.message.reply_text('Время работы: ')
    answer = get_ssh_and_run_cmd('uptime')
    update.message.reply_text(answer)
    return ConversationHandler.END  # Завершаем работу обработчика диалога


def get_df(update: Update,context):
    update.message.reply_text('Состояние файловой системы: ')
    answer = get_ssh_and_run_cmd('df -h')
    update.message.reply_text(answer)
    return ConversationHandler.END  # Завершаем работу обработчика диалога


def get_free(update: Update,context):
    update.message.reply_text('Состояние оперативной памяти: ')
    answer = get_ssh_and_run_cmd('free -h')
    update.message.reply_text(answer)
    return ConversationHandler.END  # Завершаем работу обработчика диалога


def get_mpstat(update: Update,context):
    update.message.reply_text('Информация о производительности системы: ')
    answer = get_ssh_and_run_cmd('mpstat')
    update.message.reply_text(answer)
    return ConversationHandler.END  # Завершаем работу обработчика диалога


def get_w(update: Update,context):
    update.message.reply_text('Информация о работающих пользователях: ')
    answer = get_ssh_and_run_cmd('w')
    update.message.reply_text(answer)
    return ConversationHandler.END  # Завершаем работу обработчика диалога


def get_auths(update: Update,context):
    update.message.reply_text('Информация о последних 10 входах в систему: ')
    answer = get_ssh_and_run_cmd('last | head')
    update.message.reply_text(answer)
    return ConversationHandler.END  # Завершаем работу обработчика диалога


def get_critical(update: Update,context):
    update.message.reply_text('Информация о последних 5 критических событиях: ')
    answer = get_ssh_and_run_cmd('journalctl -n 5 -p crit')
    update.message.reply_text(answer)
    return ConversationHandler.END  # Завершаем работу обработчика диалога


def get_ps(update: Update,context):
    update.message.reply_text('Информация о запущенных процессах: ')
    answer = get_ssh_and_run_cmd('ps aux | head -n 30')
    update.message.reply_text(answer)
    return ConversationHandler.END  # Завершаем работу обработчика диалога


def get_ss(update: Update,context):
    update.message.reply_text('Информация об используемых портах: ')
    answer = get_ssh_and_run_cmd('ss -tuln')
    update.message.reply_text(answer)
    return ConversationHandler.END  # Завершаем работу обработчика диалога


def get_services(update: Update,context):
    update.message.reply_text('Информация об используемых сервисах: ')
    answer = get_ssh_and_run_cmd('systemctl list-units --type=service --state=running | head -n 45')
    update.message.reply_text(answer)
    return ConversationHandler.END  # Завершаем работу обработчика диалога


import subprocess

def get_repl_logs(update: Update, context):
    update.message.reply_text("Ищу логи о репликации...")
    
    repl_logs_info = get_ssh_and_run_cmd("sudo cat /var/log/postgresql/postgresql-14-main.log | grep repl  | tail -n 35")
    
    # Отправляем найденные логи в сообщении
    update.message.reply_text(repl_logs_info)  
    return ConversationHandler.END  # Завершаем работу обработчика диалога   


def get_apt_list_command(update: Update,context):
    update.message.reply_text('Введите конкретный пакет или введите "all", чтобы вывести все пакеты: ')
    return 'get_apt_list'


def get_apt_list(update: Update,context):
    user_input = update.message.text  # получаем текст
    if user_input == 'all':
        update.message.reply_text('Информация об установленных пакетах: ')
        answer = get_ssh_and_run_cmd('apt list --installed | head -n 40')
    else:
        update.message.reply_text(f'Информация о {user_input}: ')
        answer = get_ssh_and_run_cmd(f'apt list --installed | grep {user_input} | head -n 40')
    update.message.reply_text(answer)
    return ConversationHandler.END  # Завершаем работу обработчика диалога


def connect_to_db():

    #connection = None

    DBUSER = os.getenv('DB_USER')
    DBPASSWORD = os.getenv('DB_PASSWORD')
    DBHOST = os.getenv('DB_HOST')
    DBPORT = os.getenv('DB_PORT')
    DBNAME = os.getenv('DB_DATABASE')

    try:
        connection = psycopg2.connect(user=DBUSER,
                                      password=DBPASSWORD,
                                      host=DBHOST,
                                      port=DBPORT,
                                      database=DBNAME)
        return connection

    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
        return None


def get_emails(update: Update,context):
    update.message.reply_text('Содержание таблицы о email-адресах: ')
    connection = connect_to_db()
    answer = ''
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM emails;')
            data = cursor.fetchall()
            answer = data
        except (Exception, Error) as error:
            logging.error(f"Произошла ошибка при получении email-адресов: {error}")
            update.message.reply_text('Произошла ошибка при получении email-адресов!')
        finally:
            cursor.close()
            connection.close()
            logging.info("Соединение с PostgreSQL закрыто")
    else:
        update.message.reply_text('Не удалось подключиться к базе данных!')
    real_answer = ''
    for row in answer:
        real_answer += str(row) + "\n"
    update.message.reply_text(real_answer)
    return ConversationHandler.END  # Завершаем работу обработчика диалога


def get_phone_numbers(update: Update,context):
    update.message.reply_text('Содержание таблицы о телефонах: ')
    connection = connect_to_db()
    answer = ''
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM phones;')
            data = cursor.fetchall()
            answer = data
        except (Exception, Error) as error:
            logger.error(f"Произошла ошибка при получении телефонов: {error}")
            update.message.reply_text('Произошла ошибка при получении телефонов.')
        finally:
            cursor.close()
            connection.close()
            logging.info("Соединение с PostgreSQL закрыто")
    else:
        update.message.reply_text('Не удалось подключиться к базе данных!')
    real_answer = ''
    for row in answer:
        real_answer += str(row) + "\n"
    update.message.reply_text(real_answer)
    return ConversationHandler.END  # Завершаем работу обработчика диалога


def echo(update: Update, context):
    update.message.reply_text(update.message.text)


def main():
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчик диалога
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', find_phone_number_command)],
        states={
            'find_phone_number': [MessageHandler(Filters.text & ~Filters.command, find_phone_number)],
            'save_phone_numbers': [MessageHandler(Filters.text & ~Filters.command, save_phone_numbers)],
        },
        fallbacks=[]
    )
    convHandlerFindEmails = ConversationHandler(
        entry_points=[CommandHandler('find_email', find_email_command)],
        states={
            'find_email': [MessageHandler(Filters.text & ~Filters.command, find_email)],
            'save_emails': [MessageHandler(Filters.text & ~Filters.command, save_emails)],
        },
        fallbacks=[]
    )
    convHandlerVerifyPassword = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verify_password_command)],
        states={
            'verify_password': [MessageHandler(Filters.text & ~Filters.command, verify_password)],
        },
        fallbacks=[]
    )
    convHandlerGetAptList = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', get_apt_list_command)],
        states={
            'get_apt_list': [MessageHandler(Filters.text & ~Filters.command, get_apt_list)],
        },
        fallbacks=[]
    )
    # Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmails)
    dp.add_handler(convHandlerVerifyPassword)
    dp.add_handler(CommandHandler("get_release", get_release))
    dp.add_handler(CommandHandler("get_uname", get_uname))
    dp.add_handler(CommandHandler("get_uptime", get_uptime))
    dp.add_handler(CommandHandler("get_df", get_df))
    dp.add_handler(CommandHandler("get_free", get_free))
    dp.add_handler(CommandHandler("get_mpstat", get_mpstat))
    dp.add_handler(CommandHandler("get_w", get_w))
    dp.add_handler(CommandHandler("get_auths", get_auths))
    dp.add_handler(CommandHandler("get_critical", get_critical))
    dp.add_handler(CommandHandler("get_ps", get_ps))
    dp.add_handler(CommandHandler("get_ss", get_ss))
    dp.add_handler(CommandHandler("get_services", get_services))
    dp.add_handler(CommandHandler("get_repl_logs", get_repl_logs))
    dp.add_handler(CommandHandler("get_emails",get_emails))
    dp.add_handler(CommandHandler("get_phone_numbers",get_phone_numbers))
    dp.add_handler(convHandlerGetAptList)


    # Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Запускаем бота
    updater.start_polling()

    # Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
