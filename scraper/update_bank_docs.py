import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.runner import run_all
from datetime import datetime

def update_bank_docs():
    products = run_all()
    
    if not products:
        print("Нет данных — пропускаем обновление")
        return

    # Генерируем обновлённый bank_documents.py
    content = f'''# Автогенерировано {datetime.now().strftime("%Y-%m-%d %H:%M")}
# Не редактируй вручную — данные обновляются парсером

scraped_banks = {repr(products)}
'''
    
    with open("data/scraped_banks.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"✓ Обновлено {len(products)} продуктов")

if __name__ == "__main__":
    update_bank_docs()