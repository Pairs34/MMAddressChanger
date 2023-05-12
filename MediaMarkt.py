from urllib.parse import urlencode

import requests as requests
from bs4 import BeautifulSoup
import re

class MM:

    def __init__(self):
        self.storeId = None
        self.session = requests.session()

    def visit_first(self):
        self.session.get("https://www.mediamarkt.com.tr/webapp/wcs/stores/servlet/LogonForm")

    def login(self, username: str, password: str):

        self.visit_first()

        payload_dict = {
            "storeId": 20201,
            "langId": -1,
            "rememberMe": True,
            "redirectURL": "",
            "logonId": username,
            "password": password
        }

        payload = urlencode(payload_dict, doseq=False)

        url = "https://www.mediamarkt.com.tr/webapp/wcs/stores/servlet/MultiChannelLogon"

        headers = {
            'authority': 'www.mediamarkt.com.tr',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',

            'origin': 'https://www.mediamarkt.com.tr',
            'pragma': 'no-cache',
            'referer': 'https://www.mediamarkt.com.tr/webapp/wcs/stores/servlet/LogonForm',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        if response.status_code == 200:
            print("Giriş başarılı")
        else:
            print("Giriş başarısız", response.content)

    def check_pre_basket(self, product_link: str):

        product_link_content = self.session.get(product_link)

        parser = BeautifulSoup(product_link_content.content, 'html.parser')

        product_input = parser.find("input", {"name": "contentSpotInfo-product_detail-top"})

        product_detail = {
            "catEntryId": product_input.attrs['data-catentryid'],
            "categoryId": product_input.attrs['data-categoryid'],
            "langId": -14,
            "storeId": product_input.attrs['data-storeid'],
            "quantity": 1
        }

        self.storeId = product_input.attrs['data-storeid']

        return product_detail

    def add_basket(self, product_detail: dict):

        url = f"https://www.mediamarkt.com.tr/webapp/wcs/stores/servlet/MultiChannelOrderCatalogEntryAdd?{urlencode(product_detail, doseq=False)}"

        headers = {
            'authority': 'www.mediamarkt.com.tr',
            'accept': '*/*',
            'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
        }

        response = self.session.get(url, headers=headers)

        if response.status_code == 200:
            print("Stok başarılı bir şekilde sepete eklendi")
        else:
            print("Stok sepete eklenemedi")

    def get_order_id(self):

        cookie_string = "; ".join([str(x) + "=" + str(y) for x, y in self.session.cookies.items()])

        headers = {
            'authority': 'www.mediamarkt.com.tr',
            'accept': '*/*',
            'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            # 'cookie': cookie_string,
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
        }

        basket_content = self.session.get(f"https://www.mediamarkt.com.tr/webapp/wcs/stores/servlet/MultiChannelDisplayBasket?storeId={self.storeId}&langId=-14", headers=headers)

        order_id = re.findall("orderId=\d{7,9}", basket_content.text)

        if len(order_id) > 1:
            return order_id[0].replace("orderId=", "")
        else:
            return None