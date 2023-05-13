from MediaMarkt import MM

maillist = None
with open("maillist.txt", "r") as fmail:
    maillist = fmail.read().splitlines()
    fmail.close()

print(f"{len(maillist)} adet kadar mail adresi var")

urun_linki = input("Ürün linki giriniz :") or "https://www.mediamarkt.com.tr/tr/product/_samsung-vr3mb77312k-robot-s%C3%BCp%C3%BCrge-1228770.html"

for mail_line in maillist:
    email_address = mail_line.split(":")[0]
    password = mail_line.split(":")[1]

    print(f"{email_address} için işlem yapılıyor.")

    mm = MM()
    random_city = mm.get_city()
    random_district = mm.get_district(random_city["id"])
    random_neighborhood = mm.get_district(random_district["id"])

    mm.login(email_address, password)

    basket_detail = mm.check_pre_basket(urun_linki)

    mm.add_basket(basket_detail)

    order_id = mm.get_order_id()

    mm.set_invoice_address(il=random_city, ilce=random_district, mahalle=random_neighborhood, order_id=order_id)
    mm.set_delivery_address(order_id=order_id)
    mm.finish()
