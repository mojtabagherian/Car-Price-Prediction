import sqlite3
from sklearn import tree
cnx = sqlite3.connect('learn.db')
cursor = cnx.cursor()
query = 'SELECT * FROM bama ;'
cursor.execute(query)
x = []
y = []
for (num, kilometer, price, year) in cursor:
    price1 = ''
    for i in price:
        if i == 'T' or i == 'o' or i == 'm' or i == 'a' or i == 'n' or i == ',':
            pass
        else:
            price1 += i
    price2 = int(price1)
    kilometer1 = ''
    for j in kilometer:
        if j == 'K' or j == 'i' or j == 'l' or j == 'o' or j == 'm' or j == ',' or j == 'e' or j == 't' or j == 'r':
            pass
        else:
            kilometer1 += j
    kilometer2 = int(kilometer1)
    year2 = year.strip('،')
    z = []
    z.append(kilometer2)
    z.append(year2)
    x.append(z)
    y.append(price2)

def calendar():
    if year[0] == '2':
        return 'Enter release year in latin calendar format : '
    else:
        return 'Enter release year in persian calendar format : '


clf = tree.DecisionTreeClassifier()
clf.fit(x, y)
a = int(input('Enter kilometer : '))
b = int(input(calendar()))
userdata = [[a, b]]
answer = clf.predict(userdata)
ans = ''
bagh = len(str(answer[0])) % 3
s = -bagh + 1
for i in str(answer[0]):
    ans += i
    if s == 0:
        ans += ','
    elif s % 3 == 0:
        ans += ','
    s += 1
ans = ans.strip(',')
print('Your car price is about %s Toman' % ans)
cnx.commit()
cursor.close()
cnx.close()
