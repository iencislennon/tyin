import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scraper.base import BankScraper


class ForteScraper(BankScraper):

    URL = "https://bank.forte.kz/ru/credits"

    def scrape(self) -> list[dict]:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(self.URL, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")

        products = []
        skip = ["рус", "қаз", "для вас", "для бизнеса", "premier", "forte",
                "приложение", "терминал", "банкомат", "отделение", "спасибо",
                "рассчитайте", "способы"]

        for card in soup.find_all("h3"):
            name = card.get_text(strip=True)
            if not name or len(name) < 3:
                continue
            if any(s in name.lower() for s in skip):
                continue

            description = ""
            next_span = card.find_next("span")
            if next_span:
                description = next_span.get_text(strip=True)

            product = {
                "bank": "ForteBank",
                "name": name,
                "description": description,
                "annual_rate_min": self._extract_rate_min(description),
                "annual_rate_max": self._extract_rate_max(description),
                "max_sum": self._extract_max_sum(description),
                "max_months": self._extract_max_months(description),
                "source_url": self.URL,
                "updated_at": datetime.now().isoformat(),
            }
            products.append(product)

        return products

    def _extract_rate_min(self, text: str) -> float | None:
        match = re.search(r'от\s*([\d]+[,\.][\d]+|[\d]+)\s*%', text)
        if match:
            return float(match.group(1).replace(",", "."))
        match = re.search(r'[Сс]тавка\s*([\d]+[,\.][\d]+|[\d]+)\s*%', text)
        if match:
            return float(match.group(1).replace(",", "."))
        return None

    def _extract_rate_max(self, text: str) -> float | None:
        matches = re.findall(r'до\s*([\d]+[,\.][\d]+|[\d]+)\s*%', text)
        if matches:
            return float(matches[-1].replace(",", "."))
        return None

    def _extract_max_sum(self, text: str) -> float | None:
        match = re.search(r'до\s*([\d][\d\s]*[\d])\s*₸', text)
        if match:
            return float(match.group(1).replace(" ", ""))
        match = re.search(r'([\d][\d\s]+[\d])\s*₸', text)
        if match:
            return float(match.group(1).replace(" ", ""))
        return None

    def _extract_max_months(self, text: str) -> int | None:
        match = re.search(r'до\s*(\d+)\s*месяц', text)
        if match:
            return int(match.group(1))
        match = re.search(r'(\d+)\s*месяц', text)
        if match:
            return int(match.group(1))
        match = re.search(r'(\d+)\s*лет', text)
        if match:
            return int(match.group(1)) * 12
        return None