import random
import time
from http.cookiejar import Cookie
from urllib.parse import urlencode

import requests as requests
from bs4 import BeautifulSoup
import re
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By


class MM:

    def __init__(self):

        self.driver_options = uc.ChromeOptions()
        self.driver_options.headless = True
        self.driver = uc.Chrome(options=self.driver_options, version_main=108)
        self.cookie_string = None
        self.basket = None
        self.streets = None
        self.names = None
        self.lastnames = None
        self.user_agent = None
        self.session = requests.session()
        self.load_streets()
        self.load_names()
        self.load_lastnames()

    def finish(self):
        self.cookie_string = None
        self.basket = None
        self.streets = None
        self.names = None
        self.lastnames = None
        self.user_agent = None
        self.driver.close()
        self.driver = None

    def load_streets(self):
        with open("street.txt", "r") as f:
            self.streets = f.readlines()
            f.close()

    def load_names(self):
        with open("isimler.txt", "r", encoding="utf-8") as f:
            self.names = f.read().splitlines()
            f.close()

    def load_lastnames(self):
        with open("soyisimler.txt", "r", encoding="utf-8") as f:
            self.lastnames = f.read().splitlines()
            f.close()

    def page_is_loading(self):
        while True:
            time.sleep(1)
            x = self.driver.execute_script("return document.readyState")
            if x == "complete":
                return True
            else:
                yield False

    def login(self, username: str, password: str):
        self.driver.get("https://www.mediamarkt.com.tr/webapp/wcs/stores/servlet/LogonForm")
        self.page_is_loading()

        username_el = self.driver.find_element(By.XPATH, "//input[@id='login-email']")
        pass_el = self.driver.find_element(By.XPATH, "//input[@id='login-password']")
        btn_login = self.driver.find_element(By.XPATH, "//button[@id='my-account-action-login']")

        username_el.send_keys(username)
        pass_el.send_keys(password)

        btn_login.click()

        self.page_is_loading()

        is_logged = False
        start = time.time()

        while not is_logged:
            delta = time.time() - start
            if delta >= 60:
                break

            all_cookies = self.driver.get_cookies()
            for cookie in all_cookies:
                if cookie['name'] == 'MC_SSO_TOKEN':
                    print("Giriş başarılı")
                    is_logged = True
                    break

        self.cookie_string = "; ".join([x["name"] + "=" + x["value"] for x in self.driver.get_cookies()])
        [self.session.cookies.set(c['name'], c['value']) for c in self.driver.get_cookies()]
        self.user_agent = self.driver.execute_script("return navigator.userAgent;")

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

        self.basket = product_detail

        return product_detail

    def add_basket(self, product_detail: dict):

        url = f"https://www.mediamarkt.com.tr/webapp/wcs/stores/servlet/MultiChannelOrderCatalogEntryAdd?{urlencode(product_detail, doseq=False)}"

        headers = {
            'authority': 'www.mediamarkt.com.tr',
            'accept': '*/*',
            'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'user-agent': self.user_agent
        }

        response = self.session.get(url, headers=headers)

        if response.status_code == 200:
            print("Stok başarılı bir şekilde sepete eklendi")
        else:
            print("Stok sepete eklenemedi")

    def get_order_id(self):

        headers = {
            'authority': 'www.mediamarkt.com.tr',
            'accept': '*/*',
            'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'user-agent': self.user_agent
        }

        basket_content = self.session.get(
            f"https://www.mediamarkt.com.tr/webapp/wcs/stores/servlet/MultiChannelDisplayBasket?storeId={self.basket['storeId']}&langId=-14",
            headers=headers)

        order_id = re.findall("orderId=\d{7,9}", basket_content.text)

        if len(order_id) > 1:
            return order_id[0].replace("orderId=", "")
        else:
            return None

    def get_city(self):

        city_req = requests.get(
            "https://www.mediamarkt.com.tr/webapp/wcs/stores/servlet/MultiChannelAddressSelectorValues?storeId=103452&langId=-14")

        if city_req.status_code == 200:
            city_response = city_req.json()

            return random.choice(city_response["content"])

    def get_district(self, parent_id: str):

        city_req = requests.get(
            f"https://www.mediamarkt.com.tr/webapp/wcs/stores/servlet/MultiChannelAddressSelectorValues?storeId=103452&langId=-14&parentId={parent_id}")

        if city_req.status_code == 200:
            city_response = city_req.json()

            return random.choice(city_response["content"])

    def set_invoice_address(self, il, ilce, mahalle, order_id):

        url = "https://www.mediamarkt.com.tr/webapp/wcs/stores/servlet/MultiChannelOrderSummaryController"

        first_name = random.choice(self.names)
        last_name = random.choice(self.lastnames)

        print(first_name, last_name)

        data = {
            'storeId': self.basket["storeId"],
            'langId': '-14',
            'orderId': order_id,
            'lastName': last_name,
            'street': mahalle["name"],
            'corporateForm': 'null',
            'district': ilce["name"],
            'addressAddition': '',
            'channelsactive': 'false',
            'firstLastnameCombined': f'{first_name} {last_name}',
            'country': 'Türkiye',
            'defaultCountry': 'TR',
            'loyaltyClubSelected': 'false',
            'salutation': 'Mr',
            'firstName': first_name,
            'formType': 'personal form',
            'loyaltyClubMode': 'register',
            'zip': '22700',
            'mobile': '+905555555555',
            'taxId': '25180488332',
            'privateTaxId': '25180488332',
            'isGuestRegistration': 'false',
            'housenumber': '.',
            'city': il["name"],
            'isUserRegistration': 'false',
            'showCaptcha': 'false',
            'city_id': il["id"],
            'district_id': ilce["id"],
            'county_id': '-24784',
            'isAddressComplete': 'true',
            'method': 'savePersonalData'
        }

        payload = urlencode(data, doseq=True)

        headers = {
            'authority': 'www.mediamarkt.com.tr',
            'accept': 'application/json',
            'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/x-www-form-urlencoded',
            'cookie': self.cookie_string,
            'origin': 'https://www.mediamarkt.com.tr',
            'referer': f'https://www.mediamarkt.com.tr/webapp/wcs/stores/servlet/MultiChannelOrderSummary',
            'user-agent': self.user_agent,
            'x-requested-with': 'XMLHttpRequest'
        }

        response = self.session.post(url, headers=headers, data=payload)

        if response.status_code == 200:
            print("Fatura adresi güncellendi.")
        else:
            print("Fatura adresi güncellenemedi.")

    def set_delivery_address(self, order_id):
        url = "https://www.mediamarkt.com.tr/webapp/wcs/stores/servlet/MultiChannelOrderSummaryController"

        first_name = random.choice(self.names)
        last_name = random.choice(self.lastnames)

        print(first_name, last_name)

        data = {
            'storeId': '103452',
            'langId': '-14',
            'orderId': order_id,
            'shipModeId': '-136001',
            'country': 'Türkiye',
            'salutation': 'Mr',
            'firstLastnameCombined': first_name + " " + last_name,
            'businessTitle': '',
            'firstName': first_name,
            'lastName': last_name,
            'street': 'omr ALTINOVA MH FUAR CD NO 63 BUTTİM PLAZA KAT 3 NO 304',
            'housenumber': '.',
            'addressAdditional': '',
            'district': 'Osmangazi',
            'zip': '16090',
            'city': 'Bursa',
            'city_id': '-21',
            'district_id': '-313',
            'contactPerson': '',
            'packstationNum': '.',
            'county_id': '-19242',
            'value': 'DELIVERY',
            'submethod': 'shipping',
            'method': 'saveDeliveryData'
        }

        payload = urlencode(data, doseq=True)

        headers = {
            'authority': 'www.mediamarkt.com.tr',
            'accept': 'application/json',
            'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'cookie': self.cookie_string,
            'origin': 'https://www.mediamarkt.com.tr',
            'pragma': 'no-cache',
            'referer': 'https://www.mediamarkt.com.tr/webapp/wcs/stores/servlet/MultiChannelOrderSummary',
            'user-agent': self.user_agent,
            'x-requested-with': 'XMLHttpRequest'
        }

        response = self.session.post(url, headers=headers, data=payload)

        if response.status_code == 200:
            print("Teslimat adresi güncellendi.")
        else:
            print("Teslimat adresi güncellenemedi.")
