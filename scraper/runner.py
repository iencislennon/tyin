import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.forte import ForteScraper
from scraper.cleaner import clean

def run_all() -> list[dict]:
    scrapers = [
        ForteScraper(),
        # HalykScraper(),
        # KaspiScraper(),
    ]

    all_products = []
    for scraper in scrapers:
        all_products.extend(scraper.run())

    cleaned = clean(all_products)
    print(f"\\nИтого: {len(cleaned)} продуктов")

    for p in cleaned:
        print(f"\\n{p['bank']} — {p['name']}")
        print(f"  Ставка:  {p['annual_rate_min']}% — {p['annual_rate_max']}%")
        print(f"  Сумма:   до {p['max_sum']:,.0f} тенге")
        print(f"  Срок:    до {p['max_months']} мес.")

    return cleaned

if __name__ == "__main__":
    run_all()