import re
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.sync_api import sync_playwright
from datetime import datetime
from scraper.base import BankScraper


class HalykScraper(BankScraper):

    URL = "https://halykbank.kz/credits"

    def scrape(self) -> list[dict]:
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(self.URL, timeout=30000)
            page.wait_for_load_state("networkidle")
            html = page.content()

            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")

            # Собираем ссылки на продукты
            product_links = {}
            skip = [
                "қаз", "eng", "подробнее", "кредиты", "ипотека", "автокредит",
                "урегулирование", "информация", "акция", "онлайн-рассрочка",
                "москоммерцбанк", "air astana"
            ]

            for a in soup.find_all("a", href=True):
                name = a.get_text(strip=True)
                href = a.get("href", "")
                if not name or len(name) < 5:
                    continue
                if any(s in name.lower() for s in skip):
                    continue
                if "credit" not in href.lower() and "ipoteka" not in href.lower() and "auto" not in href.lower():
                    continue
                if name not in product_links:
                    full_url = f"https://halykbank.kz{href}" if href.startswith("/") else href
                    product_links[name] = full_url

            products = []

            # Заходим на каждую страницу продукта
            for name, url in product_links.items():
                try:
                    page.goto(url, timeout=20000)
                    page.wait_for_load_state("networkidle")
                    product_html = page.content()
                    product_soup = BeautifulSoup(product_html, "html.parser")
                    
                    # Собираем весь текст страницы
                    text = product_soup.get_text(" ", strip=True)

                    product = {
                        "bank": "Halyk Bank",
                        "name": name,
                        "description": text[:5000],
                        "annual_rate_min": self._extract_rate_min(text),
                        "annual_rate_max": self._extract_rate_max(text),
                        "max_sum": self._extract_max_sum(text),
                        "max_months": self._extract_max_months(text),
                        "source_url": url,
                        "updated_at": datetime.now().isoformat(),
                    }
            
                    products.append(product)
                    print(f"  ✓ {name}")
                except Exception as e:
                    print(f"  ✗ {name}: {e}")

            browser.close()

        return products

    def _extract_rate_min(self, text: str) -> float | None:
    # "от 17,5% до 38%" или "от 5% до 18,5%"
        match = re.search(r'[Сс]тавка[^%]*от\s*([\d]+[,\.][\d]+|[\d]+)\s*%', text)
        if match:
            return float(match.group(1).replace(",", "."))
        match = re.search(r'от\s*([\d]+[,\.][\d]+|[\d]+)\s*%', text)
        if match:
            return float(match.group(1).replace(",", "."))
        # "7% (ГЭСВ"
        match = re.search(r'[Сс]тавка\s+([\d]+[,\.][\d]+|[\d]+)\s*%', text)
        if match:
            return float(match.group(1).replace(",", "."))
        return None

    def _extract_rate_max(self, text: str) -> float | None:
        # Ищем ГЭСВ максимум — "ГЭСВ от 28,8% до 45,3%"
        match = re.search(r'ГЭСВ\s+от\s+[\d,\.]+%\s+(?:по|до)\s+([\d,\.]+)%', text)
        if match:
            return float(match.group(1).replace(",", "."))
        # "до 38% (ГЭСВ" — берём до ГЭСВ
        match = re.search(r'до\s*([\d]+[,\.][\d]+|[\d]+)\s*%\s*\(ГЭСВ', text)
        if match:
            return float(match.group(1).replace(",", "."))
        return None

    def _extract_max_sum(self, text: str) -> float | None:
        # "до 8 000 000 тенге" или "8 000 000 ₸"
        # Ищем после "Максимальная сумма" или "сумма"
        match = re.search(r'[Мм]аксимальн\w+\s+сумм\w+[^₸\d]*([\d][\d\s]*[\d])\s*(?:тенге|₸)', text)
        if match:
            return float(match.group(1).replace(" ", ""))
        # "до X 000 000 тенге"
        match = re.search(r'до\s*([\d][\d\s]{4,}[\d])\s*(?:тенге|₸)', text)
        if match:
            return float(match.group(1).replace(" ", ""))
        return None

    def _extract_max_months(self, text: str) -> int | None:
    # "Максимальный срок 5 лет"
        match = re.search(r'[Мм]аксимальный\s+срок\s+(\d+)\s+лет', text)
        if match:
            return int(match.group(1)) * 12

        # "Срок займа до 25 лет"
        match = re.search(r'[Сс]рок\s+займа\s+до\s+(\d+)\s+лет', text)
        if match:
            return int(match.group(1)) * 12

        # "до 240 мес" — только если число <= 360
        match = re.search(r'до\s*(\d+)\s*мес', text)
        if match:
            val = int(match.group(1))
            if val <= 360:
                return val

        # "до 25 лет" — только если число <= 30
        match = re.search(r'до\s*(\d+)\s*лет', text)
        if match:
            val = int(match.group(1))
            if val <= 30:
                return val * 12

        return None
        return None