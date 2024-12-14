from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from PIL import Image, ImageChops, ImageEnhance
import os
import csv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import json

# Wczytanie konfiguracji emaila z pliku
with open("email_config.json", "r") as config_file:
    email_config = json.load(config_file)

EMAIL = email_config["email"]
PASSWORD = email_config["password"]
RECIPIENT = email_config["recipient"]
SMTP_HOST = "web9.aftermarket.hosting"
SMTP_PORT = 587

def send_email(subject, body, attachment_path=None):
    print(f"Wysyłanie e-maila: {subject}")
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = EMAIL
    msg['To'] = RECIPIENT

    msg.attach(MIMEText(body, 'plain'))

    if attachment_path:
        with open(attachment_path, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(attachment_path)}')
            msg.attach(part)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.sendmail(EMAIL, RECIPIENT, msg.as_string())

def save_image_diff(img1, img2, diff_path):
    print(f"Porównywanie obrazów i zapisywanie różnicy do {diff_path}")
    diff = ImageChops.difference(img1, img2)

    # Konwersja do trybu RGB, aby umożliwić podświetlenie
    diff = diff.convert("RGB")
    pixels = diff.load()

    # Oznacz zmiany kolorem czerwonym
    for y in range(diff.height):
        for x in range(diff.width):
            r, g, b = pixels[x, y]
            if r > 0 or g > 0 or b > 0:  # Jeśli piksel jest różny
                pixels[x, y] = (255, 0, 0)  # Zmieniamy na czerwony

    # Jeśli różnica jest pusta (czarna), zapisz komunikat
    if not diff.getbbox():
        print("Brak istotnych różnic wizualnych.")
        return False

    diff.save(diff_path)
    return True

def monitor_websites(csv_file, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("Rozpoczęcie monitorowania stron")

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service("/usr/bin/chromedriver")  # Podaj ścieżkę do chromedriver
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        with open(csv_file, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                url = row[0]
                print(f"Przetwarzanie strony: {url}")
                site_name = url.replace("http://", "").replace("https://", "").replace("/", "_")
                site_dir = os.path.join(output_dir, site_name)

                if not os.path.exists(site_dir):
                    os.makedirs(site_dir)

                current_screenshot_path = os.path.join(site_dir, "current.png")
                previous_screenshot_path = os.path.join(site_dir, "previous.png")
                diff_screenshot_path = os.path.join(site_dir, "diff.png")

                try:
                    driver.get(url)
                    driver.save_screenshot(current_screenshot_path)

                    if os.path.exists(previous_screenshot_path):
                        print(f"Porównywanie z poprzednim zrzutem ekranu dla {url}")
                        previous_img = Image.open(previous_screenshot_path)
                        current_img = Image.open(current_screenshot_path)

                        if save_image_diff(previous_img, current_img, diff_screenshot_path):
                            print(f"Zmiana wykryta na stronie {url}, wysyłanie e-maila.")
                            send_email(f"Zmiana wykryta na stronie {url}", f"Wykryto zmiany na stronie {url}.", diff_screenshot_path)

                    if os.path.exists(previous_screenshot_path):
                        os.remove(previous_screenshot_path)
                    os.rename(current_screenshot_path, previous_screenshot_path)

                except Exception as e:
                    print(f"Błąd podczas przetwarzania strony {url}: {e}")

    finally:
        driver.quit()

CSV_FILE = "websites.csv"  # Plik CSV z listą stron
OUTPUT_DIR = "ping-data"  # Katalog na dane

monitor_websites(CSV_FILE, OUTPUT_DIR)
