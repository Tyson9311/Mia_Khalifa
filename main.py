import os
import time
import asyncio
from telethon import TelegramClient
from telethon.errors import FloodWaitError, SessionPasswordNeededError
from telethon.tl.functions.account import ReportPeerRequest
from telethon.tl.types import (
    InputReportReasonSpam, InputReportReasonViolence,
    InputReportReasonPornography, InputReportReasonChildAbuse,
    InputReportReasonFake, InputReportReasonOther
)
from rich.console import Console
from colorama import Fore, init as colorama_init

colorama_init(autoreset=True)
console = Console()

SESSION_FOLDER = 'sessions'
LOG_FOLDER = 'logs'
LOG_FILE = os.path.join(LOG_FOLDER, 'report_log.txt')
ACCOUNTS_FILE = 'accounts.txt'

os.makedirs(SESSION_FOLDER, exist_ok=True)
os.makedirs(LOG_FOLDER, exist_ok=True)

# -------------------- Input Validators --------------------
def get_valid_int(prompt, error_msg="Invalid input. Try again.", min_val=None, max_val=None):
    while True:
        try:
            value = int(input(prompt))
            if (min_val is not None and value < min_val) or (max_val is not None and value > max_val):
                raise ValueError
            return value
        except ValueError:
            print(Fore.RED + error_msg)

def get_non_empty_input(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print(Fore.RED + "This field cannot be empty.")

# -------------------- UI Functions --------------------
def print_typing(text, delay=0.05):
    for char in text:
        print(Fore.GREEN + char, end='', flush=True)
        time.sleep(delay)
    print()

def show_banner():
    os.system("cls" if os.name == "nt" else "clear")
    banner = """
##############################################
#                                            #
#             CREATED By MgKaung             #
#                                            #
#        Telegram: @usernamevip1             #
##############################################
"""
    print_typing(banner)

def input_list(prompt, delimiter=","):
    return [item.strip().lstrip("@") for item in input(prompt).split(delimiter) if item.strip()]

def choose_reason():
    reason_map = {
        "1": InputReportReasonSpam(),
        "2": InputReportReasonViolence(),
        "3": InputReportReasonPornography(),
        "4": InputReportReasonChildAbuse(),
        "5": InputReportReasonFake(),
        "6": InputReportReasonOther()
    }
    console.print(Fore.LIGHTYELLOW_EX + "\nChoose a report reason:")
    for num, reason in reason_map.items():
        print(f" {num}. {reason.__class__.__name__.replace('InputReportReason', '')}")
    return reason_map.get(input(Fore.YELLOW + "Enter number (1-6): ").strip(), InputReportReasonSpam())

# -------------------- Core Logic --------------------
def load_accounts():
    if not os.path.exists(ACCOUNTS_FILE):
        console.print(Fore.RED + "[ERROR] accounts.txt not found")
        return []
    with open(ACCOUNTS_FILE, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def log_result(message):
    with open(LOG_FILE, 'a') as log:
        log.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
    print(message)

async def report_target(client, username, reason, count, message):
    try:
        entity = await client.get_entity(username)
        for i in range(count):
            await client(ReportPeerRequest(peer=entity, reason=reason, message=message))
            log_result(Fore.GREEN + f"[{i+1}/{count}] Reported {username}")
            await asyncio.sleep(2)
    except FloodWaitError as e:
        log_result(Fore.YELLOW + f"[WAIT] Flood wait {e.seconds}s on {username}")
        await asyncio.sleep(e.seconds)
        await report_target(client, username, reason, count, message)
    except Exception as e:
        log_result(Fore.RED + f"[ERROR] {username}: {str(e)}")

async def handle_account(index, phone, targets, reason, count, message, api_id, api_hash):
    session = os.path.join(SESSION_FOLDER, f"session_{index}")
    client = TelegramClient(session, api_id, api_hash)

    try:
        await client.start(phone=phone)
    except SessionPasswordNeededError:
        log_result(Fore.RED + f"[SKIP] 2FA enabled on {phone}")
        return
    except Exception as e:
        log_result(Fore.RED + f"[ERROR] Cannot start {phone}: {e}")
        return

    for target in targets:
        await report_target(client, target, reason, count, message)
        await asyncio.sleep(3)

    await client.disconnect()
    log_result(Fore.CYAN + f"[DONE] Finished with {phone}")
    await asyncio.sleep(5)

# -------------------- Main Entry --------------------
async def main():
    show_banner()

    api_id = get_valid_int(Fore.CYAN + "Enter your Telegram API ID: ", "Please enter a valid number.", min_val=1)
    api_hash = get_non_empty_input(Fore.CYAN + "Enter your Telegram API HASH: ")

    targets = input_list(Fore.CYAN + "\nEnter target usernames (comma-separated): ")
    reason = choose_reason()
    count = get_valid_int(Fore.CYAN + "How many times to report each target? ", min_val=1)
    message = "Violation of Telegram Terms"
    accounts = load_accounts()

    if not accounts:
        console.print(Fore.RED + "No accounts loaded. Exiting.")
        return

    tasks = [
        handle_account(index, phone, targets, reason, count, message, api_id, api_hash)
        for index, phone in enumerate(accounts)
    ]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
