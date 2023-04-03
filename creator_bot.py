import shutil
import os
import subprocess
import requests
import re


src_path = "shit_bot" #стоковый бот для копирования
#directory = "@bot_new_test"
#cash_user = 420
#bot_token = "1096243381:AAEyyZnu-FddwlaRbnwoCDoVKg1Mh-Ibs-k"


async def create_folder(cash_user, bot_token, directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

    for file in os.listdir(src_path):
        file_path = os.path.join(src_path, file)
        shutil.copy(file_path, os.path.join(directory, "" + file))

    # Read in the file
    with open(f'{directory}\\config.txt', 'r') as file :
        filedata = file.read()
    print("Before: ", filedata)

    # Replace the target string
    filedata = filedata.replace('CASH_BOOST_USER = 5', f'CASH_BOOST_USER = {cash_user}')
    filedata = filedata.replace('BOT_TOKEN = none', f'BOT_TOKEN = {bot_token}')
    print("After: ", filedata)

    # Write the file out again
    with open(f'{directory}/config.txt', 'w') as file:
        file.write(filedata)
    print("Good replace")
    command = f"cd {directory}&&python main.py"
    #command = f"python {directory}\main.py"
    subprocess.Popen(["start", "/wait", "cmd", "/K", command], shell=True)

    url = f"https://api.telegram.org/bot{bot_token}/getMe"

    headers = {
        "accept": "application/json",
        "User-Agent": "Telegram Bot SDK - (https://github.com/irazasyed/telegram-bot-sdk)"
    }

    response = requests.post(url, headers=headers)
    data = response.json()
    responseOrder = data['result']
    responseOrder1 = responseOrder['username']
    anwerLink = "@" + f"{responseOrder1}"
    return anwerLink

async def changeSettings(directory, cash_user):
    # Read in the file
    with open(f'{directory}/config.txt', 'r') as file :
        filedata = file.read()
    print("Before: ", filedata)

    # Replace the target string
    filedata = re.sub(r'^CASH_BOOST_USER\s*=\s*\d+', f'CASH_BOOST_USER = {cash_user}', filedata, flags=re.MULTILINE)
    with open(f'{directory}/config.txt', 'w') as file:
        file.write(filedata)
    print("After: ", filedata)
    print("Good replace")
    #subprocess.Popen(["cmd", "/c", f"cd {directory} && taskkill /IM cmd.exe /F && start cmd /k python main.py"])

