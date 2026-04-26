from abc import ABC, abstractmethod
from datetime import datetime

class BankScraper(ABC):

    @abstractmethod
    def scrape(self) -> list[dict]:
        pass

    def run(self) -> list[dict]:
        try:
            data = self.scrape()
            print(f"✓ {self.__class__.__name__}: {len(data)} продуктов")
            return data
        except Exception as e:
            print(f"✗ {self.__class__.__name__}: {e}")
            return []
