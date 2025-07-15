
import getpass

# 🔐 Password Check
password = getpass.getpass("🔐 Enter password to continue: ")
if password != "@Dragoon_with_Dranzer":
    print("❌ Access Denied.")
    exit()

# ✅ Main Logic (Original `main.py`)
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

def print_typing(text, delay=0.05):
    for char in text:
        print(Fore.GREEN + char, end='', flush=True)
        time.sleep(delay)
    print()

def show_banner():
    os.system("cls" if os.name == "nt" else "clear")
    banner = 