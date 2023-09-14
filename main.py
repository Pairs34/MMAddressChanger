import traceback
from time import sleep

from MediaMarkt import MM

maillist = None
with open("maillist.txt", "r") as fmail:
    maillist = fmail.read().splitlines()
    fmail.close()


def changed_emails(mail):
    with open("changedmails.txt", "w") as fmail:
        fmail.write("{}\n".format(mail))
        fmail.close()


def remove_changed_mail(mail):
    with open("maillist.txt", "r+") as f:
        d = f.readlines()
        f.seek(0)
        for i in d:
            if i != mail:
                f.write(i)
        f.truncate()


print(f"{len(maillist)} adet kadar mail adresi var")

urun_linki = input(
    "Ürün linki giriniz :") or "https://www.mediamarkt.com.tr/tr/product/_samsung-vr3mb77312k-robot-s%C3%BCp%C3%BCrge-1228770.html"

tcno = input(
    "Tc numarası giriniz (Varsayılan = 13773032994): ") or "13773032994"

for i, v in enumerate(maillist):
    try:
        mail_line = v
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

        mm.set_invoice_address(il=random_city, ilce=random_district,
                               mahalle=random_neighborhood, order_id=order_id, tc=tcno)
        mm.set_delivery_address(order_id=order_id)
        changed_emails(email_address)
        remove_changed_mail()
        mm.remove_product()
        mm.finish()

        print("50 sn beklenecek")
        sleep(50)
        print("Sonraki hesaba geçiliyor")
        i = i + 1
    except:
        i = i - 1
        traceback.print_exc()
        input("Devam etmek için bir tuşa basınız")
