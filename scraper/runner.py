import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.forte import ForteScraper
from scraper.halyk import HalykScraper
from scraper.cleaner import clean

def run_all() -> list[dict]:
    scrapers = [
        ForteScraper(),
        HalykScraper(),
        # KaspiScraper(),
    ]

    all_products = []
    for scraper in scrapers:
        all_products.extend(scraper.run())

    cleaned = clean(all_products)
    print(f"\nИтого: {len(cleaned)} продуктов")

    for p in cleaned:
        print(f"\n{p['bank']} — {p['name']}")
        print(f"  Ставка:  {p['annual_rate_min']}% — {p['annual_rate_max']}%")
        sum_str = f"{p['max_sum']:,.0f}" if p['max_sum'] else "не указана"
        print(f"  Сумма:   до {sum_str} тенге")
        months_str = str(p['max_months']) if p['max_months'] else "не указан"
        print(f"  Срок:    до {months_str} мес.")

    return cleaned

if __name__ == "__main__":
    run_all()