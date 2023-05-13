import random
from urllib.parse import urlencode

import requests as requests
from bs4 import BeautifulSoup
import re
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By


class MM:

    def __init__(self):
        self.driver = uc.Chrome()
        self.basket = None
        self.streets = None
        self.names = None
        self.lastnames = None
        self.session = requests.session()
        self.load_streets()
        self.load_names()
        self.load_lastnames()

    def load_streets(self):
        with open("street.txt", "r") as f:
            self.streets = f.readlines()
            f.close()

    def load_names(self):
        with open("isimler.txt", "r",encoding="utf-8") as f:
            self.names = f.read().splitlines()
            f.close()

    def load_lastnames(self):
        with open("soyisimler.txt", "r",encoding="utf-8") as f:
            self.lastnames = f.read().splitlines()
            f.close()

    def visit_first(self):
        self.driver.get("https://www.mediamarkt.com.tr/webapp/wcs/stores/servlet/LogonForm")

    def login(self, username: str, password: str):
        username_el = self.driver.find_element(By.XPATH("//input[@id='login-email']"))
        pass_el = self.driver.find_element(By.XPATH("//input[@id='login-password']"))
        btn_login = self.driver.find_element(By.XPATH("//button[@id='my-account-action-login']"))

        username_el.send_keys(username)
        pass_el.send_keys(password)

        btn_login.click()
        # payload_dict = {
        #     "storeId": 20201,
        #     "langId": -1,
        #     "rememberMe": True,
        #     "redirectURL": "",
        #     "logonId": username,
        #     "password": password
        # }
        #
        # payload = urlencode(payload_dict, doseq=False)
        #
        # url = "https://www.mediamarkt.com.tr/webapp/wcs/stores/servlet/MultiChannelLogon"
        #
        # headers = {
        #     'authority': 'www.mediamarkt.com.tr',
        #     'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        #     'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
        #     'cache-control': 'no-cache',
        #     'content-type': 'application/x-www-form-urlencoded',
        #     'origin': 'https://www.mediamarkt.com.tr',
        #     'pragma': 'no-cache',
        #     'referer': 'https://www.mediamarkt.com.tr/webapp/wcs/stores/servlet/LogonForm',
        #     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
        # }
        #
        # response = requests.request("POST", url, headers=headers, data=payload)
        #
        # if response.status_code == 200:
        #     print("Giriş başarılı")
        # else:
        #     print("Giriş başarısız", response.content)

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
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
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
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
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
            # 'cookie': 'JSESSIONID=0000wp6i_DZAWP9dgUO1nuY8l5o:18o069bhl; MC_DEVICE_ID=-1; MC_DEVICE_ID_EXT=-1; WC_SESSION_ESTABLISHED=true; TS014d30d0=014cde7230dd88ff9caffa7560f7c8098e123821759a10cd10fc5b184f623b769e3f8061551f1153d426b97dead8cd41fce5868a49; MC_PS_CHANNEL_ID=desktop; MC_PS_SESSION_ID=wp6i_DZAWP9dgUO1nuY8l5o; BVBRANDID=1dea6c2e-313d-4088-b50d-3aea9527e09f; BVBRANDSID=791ffbfa-0de3-4bde-8abc-c67f06eb1257; TS01c09a37030=0150c1676c4fa842e6f7910fb0f0f3ade5e5bf652c0f83da81652f11b3baa17ef6e499bc30dfca0c0e2b0a6b5f480ceb518dbf8ec8; dtCookie=v_4_srv_10_sn_D45516D0B812AE2812DD0624999B04BE_perc_100000_ol_0_mul_1_app-3A275d25ae0606b607_1; TS01e37295=014cde7230bee0f3a279dab3c135aad7b421eb1a9d4873ada283a703090352e02390b57fad992353ccfffe4a6f181eeabf8db18c50693d446238fd52332785c568f8ff5b80; MC_PS_USER_ID=1671694388749-140958; MC_USER_ID=1857380699; MC_USERTYPE=R; retailerVisitorId=28461232-f8f4-492c-981d-63995081a3c8; MC_PRIVACY=marketing; WC_AUTHENTICATION_1857380699=1857380699%2C6c8e0xY7IfJqVT%2FC%2BFxRktCm29s%3D; WC_PERSISTENT=In%2BLvB9WiCUdAB4R35ACw6Ekoww%3D%0A%3B2023-05-13+12%3A23%3A27.931_1671694388749-140958_103452_1857380699%2C-14%2CTRY%2C_103452; WC_ACTIVEPOINTER=-14%2C103452; TSdbe8a455027=08381b7c0bab200014705fb45839cfd625b8d02daaf6ebdbe61163e25b84bdd80ca234241a8874c7086990c45c1130002a80f461ddf68ef522688fff7376b1d514cf5ae8197b390370ad88c7acd5c6622c56a34ff148dc0db531b1cafd89b7e8; WC_USERACTIVITY_1857380699=1857380699%2C103452%2C0%2Cnull%2C1683973411917%2C1683977574265%2Cnull%2Cnull%2Cnull%2Cnull%2Cj%2FTNVDlhrvW55K%2BY1%2BrdHTH9TZMb%2BwcBWb49WvyfJZ98HUWKnpptVhxy8azLxtWEHctm8NFe7y%2FZuOaqoNd2VwBJ%2BSXmwlJdb8GC73DXsWVkRqnj7dToJ%2F6l1BZytrEaOLdHiTJ%2FGFBhzy8TFaNOp0XpyqHfthZ0FP5xV6LHPPXlq3KJ8%2BWJRdSjN3FdINs76UIMBpPv2Mnuh%2BjzOpV1QQiecTySNLWsmbBSznUUXUI%3D; TS01c09a37=014cde72304c12033d42006b1a1a893229a99ff7c3a34a907f83e5de1b418431290a6e211a7f0780b2b2faa433344dc0d7a5bd8ef5; MC_SSO_TOKEN=pdK3lFBIuj8ynpUrd%252F50HeN1rLVXiJQqur4XsVdqUT2Z5d9PTM%252BoO83o5y7rFJ4raTGSm0c80ipx6gMU1mf%252FcX6cul9pU4pkeiul%252B9vus80%253D; TS0173859f=014cde723058edd3a0aaed5fdedc277b7b5761f4357941f832b5d2f52f1f5c0be7bb4d4569bbbf63ba3803a19d24303938039ee67a; JSESSIONID=0000mlS7spza8gLxOJbvn0reqIJ:1cleak1rs; TS01c09a37=014cde723026e566cf9d5c216fa526b7cc96a1a4e99495b63ffd3ee19514f40bbaf1e62c29ce239f4591a5098c82f7d4d900e4134d; TSef0f0ccc027=08381b7c0bab20002b8cfef01b42a6f33a9b3bcd8cbc8154d240787663ebdd2fbe6d93eb95ca25d7084bd0825c11300001bf79e1d3f29d0513526b694c821fe0b1e9eba146739b0ff39c74bcc1913d57141320f7827266ac77bb1a81f1006374; WC_ACTIVEPOINTER=-14%2C103452; WC_PERSISTENT=9jzDiY3TtqchK6yqNMCk8y%2F%2BQnc%3D%0A%3B2023-05-13+12%3A25%3A07.873_1683957828569-277325_103452; WC_USERACTIVITY_1857380699=1857380699%2C103452%2C0%2Cnull%2C1683973411917%2C1683978514176%2Cnull%2Cnull%2Cnull%2Cnull%2Cb067B%2BNV87R7mS4m92n8YBC%2FDCZGZHTjXRmwU7kXMUfSewk8%2Fl7BgmnApzT0Aifc4UUyMZmttXwplVP6YIY84sLY3qfkQviw8tGlScg8xLSFVbIcJNr0iBIRnoiXh9pGQn8aa3kWjo1txoEjsBqZdfBLMjm9AB2qZTShdclONUYbtazCcjMhp6fFuuLEzvn76epAxPNpZUwbU9QwVVsczHWhzIsQVhu%2BzSx782hOGU4%3D',
            'cookie': "JSESSIONID=0000wp6i_DZAWP9dgUO1nuY8l5o:18o069bhl; MC_DEVICE_ID=-1; MC_DEVICE_ID_EXT=-1; WC_SESSION_ESTABLISHED=true; TS014d30d0=014cde7230dd88ff9caffa7560f7c8098e123821759a10cd10fc5b184f623b769e3f8061551f1153d426b97dead8cd41fce5868a49; MC_PS_CHANNEL_ID=desktop; BVBRANDID=1dea6c2e-313d-4088-b50d-3aea9527e09f; TS01c09a37030=0150c1676c4fa842e6f7910fb0f0f3ade5e5bf652c0f83da81652f11b3baa17ef6e499bc30dfca0c0e2b0a6b5f480ceb518dbf8ec8; dtCookie=v_4_srv_10_sn_D45516D0B812AE2812DD0624999B04BE_perc_100000_ol_0_mul_1_app-3A275d25ae0606b607_1; TS01e37295=014cde7230bee0f3a279dab3c135aad7b421eb1a9d4873ada283a703090352e02390b57fad992353ccfffe4a6f181eeabf8db18c50693d446238fd52332785c568f8ff5b80; MC_PS_USER_ID=1671694388749-140958; MC_USER_ID=1857380699; MC_USERTYPE=R; retailerVisitorId=28461232-f8f4-492c-981d-63995081a3c8; MC_PRIVACY=marketing; WC_AUTHENTICATION_1857380699=1857380699%2C6c8e0xY7IfJqVT%2FC%2BFxRktCm29s%3D; WC_PERSISTENT=In%2BLvB9WiCUdAB4R35ACw6Ekoww%3D%0A%3B2023-05-13+12%3A23%3A27.931_1671694388749-140958_103452_1857380699%2C-14%2CTRY%2C_103452; WC_ACTIVEPOINTER=-14%2C103452; TSdbe8a455027=08381b7c0bab200014705fb45839cfd625b8d02daaf6ebdbe61163e25b84bdd80ca234241a8874c7086990c45c1130002a80f461ddf68ef522688fff7376b1d514cf5ae8197b390370ad88c7acd5c6622c56a34ff148dc0db531b1cafd89b7e8; MC_PS_SESSION_ID=wp6i_DZAWP9dgUO1nuY8l5o; TS01c09a37=014cde7230903b4347e20931c122dffcc62c02bc87d3a75841aca69f2109c5c4e0fb359a00a51cece1bfe96127f834f8d53abc3ae9; TS0173859f=014cde7230f1a9e079813d5a2e792acd061f1468e2838e1984758f50d6371911719489c672d2a56996d0dcf6d2165cf7193c4f430b; WC_USERACTIVITY_1857380699=1857380699%2C103452%2C0%2Cnull%2C1683973411917%2C1683980681087%2Cnull%2Cnull%2Cnull%2Cnull%2CDpY8mVri%2F8yREAzwg3VkBqQiSSJ3CdHrAvmhMa2nCH9THxTom2%2F1LHXW3zh73Mw1osUgAVFza5y5B%2BzLw649fJrFYEnuBDSLFYtL6XkNep9gnpzl6MJLuwR5NRZWbuky05x%2BcCkDmajp%2F8HoCXCENtoBMYQQwr7Bl%2BKhI2eiqHGXJBPmNJibZd0Bx7hjRZ6M5P1EQ4PUyo3B0Y8HxgFju94zX53ToTM5ZvVXOXM2ECQ%3D; MC_SSO_TOKEN=pdK3lFBIuj8K0tO1af3SqOcpYAMFqJNQ9ZveVEkAP9l8Qp41R4FH0U9ZEYifrJig%252Bhwoh8Vot%252BhAcdlUicFhAnxFnpFLlEDKmtUZFaD96IA%253D; TSef0f0ccc027=08381b7c0bab2000a85678d9f27d53df9a5b6241b7c1e23df7d71b4308869a50f1eb91f4f0cd7850088870c30b113000342a0a4c9a038cbdaafcfed7772d2b0caa91eb0ba5638a9e3959618bb0eccc29c0574cec6bc8f7d4303090d62bd6c185",
            'origin': 'https://www.mediamarkt.com.tr',
            # 'referer': f'https://www.mediamarkt.com.tr/webapp/wcs/stores/servlet/MultiChannelOrderSummary?storeId=103452&orderId=579805653&langId=-14',
            'referer': f'https://www.mediamarkt.com.tr/webapp/wcs/stores/servlet/MultiChannelOrderSummary',
            'sec-ch-ua': '"Brave";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
        }

        response = self.session.post(url, headers=headers, data=payload)

        if response.status_code == 200:
            print("Fatura adresi güncellendi.")
        else:
            print("Fatura adresi güncellenemedi.")
