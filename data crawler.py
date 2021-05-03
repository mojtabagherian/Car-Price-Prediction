import re
import requests
import sqlite3
from bs4 import BeautifulSoup
from difflib import get_close_matches
import time
# request address for get a dictionary of keys = car brands in persian and values = car brands in english
html = ''
while html == '':
    try:
        html = requests.get("https://bama.ir/car")
        break
    except:
        print("Connection refused by the server..")
        print("Let me sleep for 5 seconds")
        time.sleep(5)
        continue

bsObj = BeautifulSoup(html.text, 'html.parser')
dictt = {}
for i in range(85):
    per_name = bsObj.find('li', attrs={'id': 'brand-%i' % i})
    if per_name:
        key1 = per_name.find('span')
        key = key1.text
        value0 = per_name.find('a')
        value1 = value0.get('href')
        value2 = value1.split('/')
        value = value2[2]
        dictt[key] = value
# check users persian input for spelling and propose correct form of word


def retrive_definition(word):
    if word in dictt:
        return dictt[word]
    elif len(get_close_matches(word, dictt.keys())) > 0:
        act = input("Did you mean %s instead? [y or n]: " % get_close_matches(word, dictt.keys())[0])
        if act == "y":
            return dictt[get_close_matches(word, dictt.keys())[0]]
        elif act == "n":
            word = input('Please try again in persian : ')
            return retrive_definition(word)
        else:
            return "We don't understand your entry. Apologies."
    else:
        print('Apologize, we have not this brand of car in our website . ')
        word = input('Please try again in persian : ')
        return retrive_definition(word)


# request address for get a list of all car brands+models+sub models as address
html = requests.get("https://bama.ir")
bObj = BeautifulSoup(html.text, 'html.parser')
links_lst = []
links_lst.append('/car/alfa-romeo/4c')
links_lst.append('/car/alfa-romeo/mito')
links_lst.append('/car/alfa-romeo/giulietta')
for link in bObj.find_all('a'):
    link1 = link.get('href')
    if type(link1) == str:
        s = re.search(r'/car/\w+/\w+', link1)
        if s:
            if link1 not in links_lst:
                links_lst.append(link1)

# get users input as car brand in persian
print('Your car name consists of its brand and its model; so , please at first enter brand and then its model!')
brand1 = input("Please enter the brand of your car in persian : ")
brand = retrive_definition(brand1)

# extract models of users input brand
for i in links_lst:
    if re.findall(brand, i):
        ii = i.split('/')
        if len(ii) <= 4:
            print(ii[3])
        if len(ii) == 5:
            print('%s %s' % (ii[3], ii[4]))
    if re.findall(brand, i.title()):
        ii = i.split('/')
        if len(ii) <= 4:
            print(ii[3])
        if len(ii) <= 5:
            print('%s %s' % (ii[3], ii[4]))
    if re.findall(brand, i.upper()):
        ii = i.split('/')
        if len(ii) <= 4:
            print(ii[3])
        if len(ii) <= 5:
            print('%s %s' % (ii[3], ii[4]))

# get model of car brand as input from user
model1 = input('Please choose exactly one of above models of your car brand : ')
model = model1


# convert model or model+sub model to correct address
def two_part_model(models):
    model2 = models.split(' ')
    model_fi = '%s/%s' % (model2[0], model2[1])
    return model_fi


if ' ' in model1:
    model = two_part_model(model1)
    address = '/car/%s/%s?' % (brand, model)
# get access the user specific address for extracting sell items
else:
    address = '/car/%s/%s/all-trims?' % (brand, model)
r = requests.get('https://bama.ir' + address)
soup = BeautifulSoup(r.text, 'html.parser')
s = soup.find_all('div', attrs={'class': "listdata"})

# counter of sell items that have both price and kilometer
# counter for stop loop until 100
counter = 0
time.sleep(1)
# create table and open cursor for enter parameters into table
cnx = sqlite3.connect('learn.db')
cursor = cnx.cursor()
# cursor.execute(' DROP TABLE bama;')
try:
    cursor.execute("DROP TABLE bama;")
except:
    pass
cursor.execute(' CREATE TABLE bama (Num INT, kilometer varchar(50), price varchar(50),year varchar(40));')
# while for open new page of that address
page = 1
while counter < 1000:
    r = requests.get('https://bama.ir'+address+('page=%i' % page))
    # print(address+('page=%i' % page))
    soup = BeautifulSoup(r.text, 'html.parser')

    action = soup.find('form', attrs={'action': (address+('page=%i' % page))})
    if action is None:
        break
    s = soup.find_all('div', attrs={'class': "listdata"})
    # print(' page is ',page)
    # filtering just items that are string and have price and meter

    for f in s:
        zz = f.find('div', attrs={"class": "clearfix web-milage-div"})

        pp = f.find('p', attrs={"class": "cost"})
        # print(pp,'pp')
        # print(zz,'zz')
        if re.findall(r'حواله', zz.text):
            continue
        if re.findall(r'توافقی', pp.text):
            continue
        if re.findall(r'ماهانه', zz.text):
            continue
        if re.findall(r'ماهانه', pp.text):
            continue
        if re.findall(r'تماس', pp.text):
            continue
        if re.findall(r'پیش', pp.text):
            continue
        if re.findall(r'توضیحات', pp.text):
            continue
        else:
            price1 = f.find('p', attrs={"class": "cost"})
            price = price1.text.strip()
            milage2 = f.find('p', attrs={"class": "price milage-text-mobile visible-xs price-milage-mobile"})
            year1 = f.find('span', attrs={'itemprop': 'releaseDate'})
            year = year1.text.strip()
            if milage2 is None:
                break
            milage1 = milage2.text.strip().split(' ')
            # change the persian number to mathematical form  and separate numerical part
            if milage1[1] == 'صفر':
                milage1[1] = '0'
                milage = '%s %s %s' % (milage1[0], milage1[1], milage1[2])
            else:
                milage = milage2.text.strip()

            for_show = '%s %s %s' % (milage, price, year)
            counter += 1
            # enter parameters into created table
            karkard = milage.split(' ')
            price = price.split(' ')
            price = '%s Toman' % price[0]
            karkard = '%s Kilometer' % karkard[1]
            cursor.execute('INSERT INTO bama VALUES (\'%i\',\'%s\',\'%s\',\'%s\')' % (counter, karkard, price, year))
        # break until arrive to 100 items
        if counter == 1000:
            break

    # break when items of the page are under 12. because in next page the address converts to a mistake address
    if len(s) == 30:
        page += 1
    else:
        print("There is no more relative data's .")
        break
# show table data's to user
query = 'SELECT * FROM bama ;'
cursor.execute(query)
for (num, kilometer, price, year) in cursor:
    print(num, kilometer, price, year)

cnx.commit()
cursor.close()
cnx.close()
