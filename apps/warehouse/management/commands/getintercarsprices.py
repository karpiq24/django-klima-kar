import requests
import time

from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand
from django.db.models import Q

from apps.warehouse.models import Ware


class Command(BaseCommand):
    help = "Get retail prices from Inter Cars"

    def add_arguments(self, parser):
        parser.add_argument("path")

    def handle(self, *args, **options):
        with open(options["path"]) as f:
            lines = f.readlines()
        for line in lines:
            index = line.strip()
            ware = Ware.objects.get(Q(index=index) | Q(index_slug=Ware.slugify(index)))
            if ware.retail_price:
                continue
            time.sleep(6)
            print(f"Loading price for {ware}")
            ware.retail_price = self.get_retail_price(index)
            ware.save()
            print(ware.retail_price)
            print("----------")

    def get_retail_price(self, index):
        url = f"https://e-katalog.intercars.com.pl/oferta/0,0,{index}_szukaj/100001/"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                " Chrome/75.0.3770.80 Safari/537.36"
            )
        }
        r = requests.post(url, headers=headers)
        soup = BeautifulSoup(r.content, "html5lib")
        frames = soup.find_all("div", {"class": "product-frame"})
        for frame in frames:
            product_idx = (
                frame.find("p", {"class": "product-title", "itemprop": None})
                .find("b")
                .text
            )
            if product_idx != index:
                continue
            product_price = float(
                frame.find("b", {"itemprop": "price"}).text.split(" ")[0]
            )
            return product_price
        return None
