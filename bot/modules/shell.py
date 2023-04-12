import shlex
from subprocess import Popen, PIPE
from telegram.ext import CommandHandler
from bot import LOGGER, dispatcher
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import sendMessage, deleteMessage

def shell(update, context):
    message = update.effective_message
    cmd = message.text.split(maxsplit=1)
    if len(cmd) == 1:
        return message.reply_text('No command to execute was given.', parse_mode='HTML')
    cmd = cmd[1].strip()
    process = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = process.communicate()
    reply = ''
    stderr = stderr.decode()
    stdout = stdout.decode()
    if len(stdout) != 0:
        reply += f"*Stdout*\n`{stdout}`\n"
        LOGGER.info(f"Shell - {cmd} - {stdout}")
    if len(stderr) != 0:
        reply += f"*Stderr*\n`{stderr}`\n"
        LOGGER.error(f"Shell - {cmd} - {stderr}")
    if len(reply) > 3000:
        with open('shell_output.txt', 'w') as file:
            file.write(reply)
        with open('shell_output.txt', 'rb') as doc:
            context.bot.send_document(
                document=doc,
                filename=doc.name,
                reply_to_message_id=message.message_id,
                chat_id=message.chat_id)
    elif len(reply) != 0:
        message.reply_text(reply, parse_mode='Markdown')
    else:
        message.reply_text('No Reply', parse_mode='Markdown')


def up(update, context):
    message = update.effective_message
    args = update.message.text.split(" ", maxsplit=1)
    link = ''
    if len(args) == 1:
        return message.reply_text('Upload on GDrive or Download from GDrive...', parse_mode='HTML')
    if len(args) > 1:
        link = args[1]
        msg = sendMessage("Uploading! Please Wait...", context.bot, update.message)
        cmd = f"python3 web/aio.py {shlex.quote(link)}"
    process = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = process.communicate()
    reply = ''
    stdout = stdout.decode()
    deleteMessage(context.bot, msg)
    if len(stdout) != 0:
        reply += f"*Your File Uploaded Successfully...*\n\n*Link*: `{stdout}`\n"
    if len(reply) != 0:
        message.reply_text(reply, parse_mode='Markdown')
    else:
        message.reply_text('This file is not available on server. Check Again..', parse_mode='Markdown')

def dl(update, context):
    message = update.effective_message
    args = update.message.text.split(" ", maxsplit=1)
    link = ''
    if len(args) == 1:
        return message.reply_text('Download an Index, GDrive or any valid Direct Link to Server...', parse_mode='HTML')
    if len(args) > 1:
        link = args[1]
        msg = sendMessage("Downloading!! Please Wait...", context.bot, update.message)
    if "drive.google.com" in link:
        cmd = f"bash web/gdown {shlex.quote(link)}"
    else:
        cmd = f"bash web/aria2c {shlex.quote(link)}"
    process = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = process.communicate()
    reply = ''
    stdout = stdout.decode()
    deleteMessage(context.bot, msg)
    if len(stdout) != 0:
        reply += f"*Your File Downloaded Successfully...*\n\n*Name*: `{stdout}`\n"
    if len(reply) != 0:
        message.reply_text(reply, parse_mode='Markdown')
    else:
        message.reply_text('Not a valid Direct Link. Check Again..', parse_mode='Markdown')

def lh(update, context):
    message = update.effective_message
    args = update.message.text.split(" ", maxsplit=1)
    link = ''
    if len(args) == 1:
       return message.reply_text('Send a FileName with command to get Herokuapp.com Link...', parse_mode='HTML')
    if len(args) > 1:
        link = args[1]
        cmd = f"bash web/lh {shlex.quote(link)}"
    process = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = process.communicate()
    reply = ''
    stdout = stdout.decode()
    if len(stdout) != 0:
        reply += f"`{stdout}`"
    if len(reply) != 0:
      message.reply_text(reply, parse_mode='Markdown')


SHELL_HANDLER = CommandHandler(BotCommands.ShellCommand, shell,
                               filters=CustomFilters.owner_filter | CustomFilters.sudo_user)
R_HANDLER = CommandHandler(BotCommands.RCommand, shell,
                               filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
DL_HANDLER = CommandHandler(BotCommands.DlCommand, dl,
                               filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
UP_HANDLER = CommandHandler(BotCommands.UpCommand, up,
                               filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
LH_HANDLER = CommandHandler(BotCommands.LhCommand, lh,
                               filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
dispatcher.add_handler(SHELL_HANDLER)
dispatcher.add_handler(R_HANDLER)
dispatcher.add_handler(DL_HANDLER)
dispatcher.add_handler(UP_HANDLER)
dispatcher.add_handler(LH_HANDLER)
