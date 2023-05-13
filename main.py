from MediaMarkt import MM

mm = MM()

random_city = mm.get_city()
random_district = mm.get_district(random_city["id"])
random_neighborhood = mm.get_district(random_district["id"])

mm.login("a.yldrm@outlook.com.tr", "Yldrm!34")

basket_detail = mm.check_pre_basket("https://www.mediamarkt.com.tr/tr/product/_x515ea-bq2293w-core-i3-1115g4-i%C5%9Flemci-4gb-ram-128gb-ssd-15-6-w%C4%B1n11-laptop-gri-1222608.html")

mm.add_basket(basket_detail)

order_id = mm.get_order_id()

mm.set_invoice_address(il=random_city, ilce=random_district, mahalle=random_neighborhood, order_id=order_id)

print(order_id)