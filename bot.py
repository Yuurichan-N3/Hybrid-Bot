import requests
import logging
import time
import random
import re
from concurrent.futures import ThreadPoolExecutor
from requests.adapters import HTTPAdapter, Retry
from rich.console import Console
from rich.logging import RichHandler

# Setup rich console dan logging
console = Console()
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%H:%M:%S]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("HybridBot")

# Banner
console.print("""
╔══════════════════════════════════════════════╗
║       🌟 HYBRID BOT - Automation Master      ║
║   Automate your Hybrid tasks with ease!      ║
║  Developed by: https://t.me/sentineldiscus   ║
╚══════════════════════════════════════════════╝
""", style="bold cyan")

# Hardcode user-agent
USER_AGENT = "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36"

def read_file(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

def extract_id_username(query):
    match_id = re.search(r'"id"%3A(\d+)', query)
    match_username = re.search(r'"username"%3A%22(.*?)%22', query)
    tg_id = match_id.group(1) if match_id else "tidak diketahui"
    username = match_username.group(1) if match_username else "tidak diketahui"
    return tg_id, username

def get_headers(initdata):
    tg_id, username = extract_id_username(initdata)
    return {
        "sec-ch-ua-platform": random.choice(["\"Android\"", "\"iOS\"", "\"Mac OS\""]),
        "sec-ch-ua": f"\"Chromium\";v=\"{random.randint(100, 131)}\", \"Safari\";v=\"{random.randint(12, 15)}\", \"Not?A_Brand\";v=\"99\"",
        "sec-ch-ua-mobile": "?1",
        "user-agent": USER_AGENT,
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json",
        "origin": "https://hybrid-bot.buildonhybrid.com",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://hybrid-bot.buildonhybrid.com/",
        "Tg-ld": tg_id,
        "Username": username,
        "Initdata": initdata,
        "accept-language": "en,vi-VN;q=0.9,vi;q=0.8,en-US;q=0.7",
        "priority": "u=1, i"
    }

def create_session_with_retry():
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def process_account(index, initdata):
    session = create_session_with_retry()
    headers = get_headers(initdata)
    logger.info(f"==== Memproses akun {index + 1} ====")

    # Opsi 1: Ambil dan mulai tugas
    url_level = "https://bot-back.buildonhybrid.com/api/tasks/my"
    url_task_start = "https://bot-back.buildonhybrid.com/api/tasks/start/{taskid}"
    try:
        response = session.get(url_level, headers=headers)
        logger.info(f"[Akun {index + 1}] Kode Status Tugas: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            available_tasks = data.get("available", [])
            if not available_tasks:
                logger.warning(f"[Akun {index + 1}] Tidak ada tugas!")
            for task in available_tasks:
                task_id = task.get("id")
                task_name = task.get("description", "Tugas Tanpa Deskripsi")  # Menggunakan "description" sebagai nama tugas
                if task_id:
                    logger.info(f"[Akun {index + 1}] Memulai Tugas: {task_name}")
                    start_url = url_task_start.format(taskid=task_id)
                    response_start = session.post(start_url, headers=headers)
                    logger.info(f"[Akun {index + 1}] Status {task_name}: {response_start.status_code}")
                    time.sleep(1)
        else:
            logger.warning(f"[Akun {index + 1}] Gagal mengambil data tugas.")
    except requests.RequestException as e:
        logger.error(f"[Akun {index + 1}] Kesalahan tugas: {e}")

    # Opsi 3: Klaim dan mulai farming
    url_claim = "https://bot-back.buildonhybrid.com/api/farming/claim"
    url_start = "https://bot-back.buildonhybrid.com/api/farming/start"
    try:
        response_claim = session.post(url_claim, headers=headers)
        logger.info(f"[Akun {index + 1}] Klaim: {response_claim.status_code}")
        time.sleep(1)
        response_start = session.post(url_start, headers=headers)
        logger.info(f"[Akun {index + 1}] Mulai Farming: {response_start.status_code}")
    except requests.RequestException as e:
        logger.error(f"[Akun {index + 1}] Kesalahan farming: {e}")

def main():
    initdata_list = read_file("data.txt")
    
    while True:
        console.print("[bold yellow]Memulai proses otomatis...[/]")
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(process_account, i, initdata) for i, initdata in enumerate(initdata_list)]
            for future in futures:
                future.result()  # Tunggu semua thread selesai
        console.print("[bold green]Selesai memproses semua akun![/]")
        
        # Tunggu 6 jam 5 menit (6 * 3600 + 5 * 60 = 21,900 detik)
        wait_time = 6 * 3600 + 5 * 60
        console.print(f"[bold blue]Menunggu {wait_time // 3600} jam {(wait_time % 3600) // 60} menit sebelum proses berikutnya...[/]")
        time.sleep(wait_time)

if __name__ == "__main__":
    main()
