from django.shortcuts import render
from django.http import HttpResponse
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as uReq
import pandas as pd
import concurrent.futures
from wordcloud import WordCloud
from .models import NewUser
from django.contrib import messages

filename = "all_products.csv"
f = open(filename, "w")
headers = "Product Name,Pricing(Rs.),Ratings,Popularity,Reviews,Ram(GB),ROM(GB),Brand,URL\n"
f.write(headers)
in_url = list()
rev = ""
def scrap3(url2):
    print(url2)
    global rev
    uClient = uReq(url2)
    page_html = uClient.read()
    uClient.close()
    page_soup = soup(page_html, "html.parser")
    containers = page_soup.findAll("div", {"class": "t-ZTKy"})
    reviews = ""
    for i in range(len(containers) - 1):
        reviews = reviews + ' ' + containers[i].div.text[:-9]
    rev += reviews


def scrap1(url2):
    uClient = uReq(url2)
    page_html = uClient.read()
    uClient.close()
    page_soup = soup(page_html, "html.parser")
    cotainer = page_soup.findAll("div", {"class": "_2kHMtA"})


    for con in cotainer:
        if con.div.img is not None:
            product_name = con.div.img["alt"]
            link1 = con.a['href']
            link1 = 'https://flipkart.com' + link1
            brand_s = product_name.split(" ")
            brand = brand_s[0]
            price_con = con.findAll("div", {"class": "_30jeq3 _1_WHN1"})
            if len(price_con) != 0:
                price = price_con[0].text.strip()
                trim_price = ''.join(price.split(','))
                rm_rupee = trim_price.split("₹")
                add_rs = "" + rm_rupee[1]
                new = add_rs.split("E")
                new1 = new[0].split("N")
                final_price = new1[0]
            else:
                final_price = ""
            rat_con = con.findAll("div", {"class": "gUuXy-"})
            if len(rat_con) != 0:
                rat = rat_con[0].text
                final_rat = rat[0:3]
                pop = rat.split(" ")
                final_rew = pop[1][10:]
                final_pop = pop[0][3:]
            else:
                final_rew = ""
                final_rat = ""
                final_pop = ""
            ram_rom = con.findAll("div", {"class": "fMghEO"})
            if len(ram_rom) != 0:
                ram = ram_rom[0].text
                ram_split = ram.split(" ")
                final_rom = ram_split[4]
                final_ram = ram_split[0]
            else:
                final_rom = ""
                final_ram = ""



            f.write(product_name.replace(",", "|") + "," + final_price + "," + final_rat + "," + final_pop.replace(",","") + ","
                        + final_rew.replace(",", "") + "," + final_ram + "," + final_rom + "," + brand + "," + link1 + "\n")



def scrap2(url3):
    uClient = uReq(url3)
    page_html = uClient.read()
    uClient.close()
    page_soup = soup(page_html, "html.parser")
    container = page_soup.find("div", {"class": "col JOpGWq"})
    download = container.find_all('a')
    link1 = "https://www.flipkart.com" + download[-1]['href']
    in_url.append(link1)



def home(request):
    return render(request, 'MyProject/home.html')

def log1(request):
    return render(request, 'MyProject/index.html')

def sign1(request):
    if request.method == 'POST':
        name = request.POST['name']
        phone = request.POST['phone']
        email = request.POST['email']
        password = request.POST['password']
        NewUser(name=name, phone=phone, email=email, password=password).save()
        messages.success(request, "SignUp Successfully !!!")
        return render(request, 'MyProject/register.html')
    else:
        return render(request, 'MyProject/register.html')


def log2(request):
    if request.method == 'POST':
        try:
            Userdetails = NewUser.objects.get(email=request.POST['email'], password=request.POST['password'])
            print("Username = ", Userdetails)
            request.session['email'] = Userdetails.email
            return render(request, 'MyProject/home.html')
        except NewUser.DoesNotExist as e:
            messages.success(request, "Email Id/Password Invalid ... !")

    return render(request, 'MyProject/index.html')

def reg1(request):
    return render(request, 'MyProject/register.html')

def lout1(request):
    try:
        del request.session['email']
    except:
        return render(request, 'MyProject/home.html')
    return render(request, 'MyProject/home.html')


def print1(request):
    search = request.GET['num1']
    pfrom = 15000
    pto = 20000
    search = search.replace(" ","+")
    print(search)
    my_url = 'https://www.flipkart.com/search?q=' + search + '&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off&page='

    uClient = uReq(my_url)
    page_html = uClient.read()
    uClient.close()
    page_soup = soup(page_html, "html.parser")

    cotainer = page_soup.findAll("div", {"class": "_2kHMtA"})

    pages = 0
    pages = page_soup.findAll("div", {"class": "_2MImiq"})
    count = 1
    if len(pages) != 0:
        count = int(pages[0].span.text[-2:])

    if count>5:
        count = 5
    urls_list = []
    for i in range(1, count + 1):
        my_url = 'https://www.flipkart.com/search?q=' + search + '&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off&page=' + str(
            i)
        urls_list.append(my_url)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(scrap1, urls_list)
    f.close()

    data = pd.read_csv('all_products.csv', encoding='unicode_escape', error_bad_lines=False)
    data = data.dropna(axis=0)
    data = data[data['Pricing(Rs.)'].between(pfrom, pto, inclusive=True)]
    avg_price = data['Pricing(Rs.)'].mean()
    avg_rat = data['Ratings'].mean()
    avg_pop = data['Popularity'].mean()
    avg_rev = data['Reviews'].mean()
    data['buy_prob'] = 0
    data = data.head(10)
    print(avg_price)
    for ind in data.index:
        print(data['Popularity'][ind], data['Ratings'][ind])

        if data['Pricing(Rs.)'][ind] <= avg_price:
            data['buy_prob'][ind] += 1
        else:
            data['buy_prob'][ind] += 0.5

        if data['Ratings'][ind] >= avg_rat:
            data['buy_prob'][ind] += 1
        else:
            data['buy_prob'][ind] += 0.5

        if data['Popularity'][ind] >= avg_pop:
            data['buy_prob'][ind] += 1
        else:
            data['buy_prob'][ind] += 0.5

        if data['Reviews'][ind] >= avg_rev:
            data['buy_prob'][ind] += 1
        else:
            data['buy_prob'][ind] += 0.5
    data.sort_values(by=['buy_prob'], inplace=True, ascending=False)
    data = data.dropna(axis=0)
    data = data.reset_index(drop=True)
    lst = list()
    to_url = list()
    for l in data.iterrows():
        to_url.append(l[1][8])
    print(to_url)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(scrap2, to_url)

    data['in_URL'] = pd.Series(in_url)
    print(in_url)
    for l in data.iterrows():
        temp = [l[1][0], l[1][1], l[1][2], l[1][3], l[1][4], l[1][5], l[1][6], l[1][7], l[1][8], l[1][10]]
        '''amz1 = temp[0]

        amz = amz1.replace("(", "%28")
        amz = amz.replace(")", "%29")
        amz = amz.replace(",", "%2C")
        amz = amz.replace(" ", "+")
        a_url = 'https://www.amazon.in/s?k=' + amz + '&ref=nb_sb_noss_2'
        uClient = uReq(a_url)
        page_html = uClient.read()
        uClient.close()
        page_soup = soup(page_html, "html.parser")
        print("in")

        pric = page_soup.findAll("span", {"class": "a-price-whole"})
        price = pric[0].text
        price = price.replace(",","")
        print("inside")

        #a_link = a_cotainer[0].find("a", {"class": "a-link-normal a-text-normal"})
        #a_link = "https://www.amazon.in" + a_link['href']

        if int(price) < int(temp[1]):
            print("forrrrrrrrrrrr")
            temp[1] = price
            #temp[8] = a_link'''

        lst.append(temp)

    return render(request, 'MyProject/result.html', {'list': lst})


def word1(request):
    url = request.GET['link11']
    uClient = uReq(url)
    page_html = uClient.read()
    uClient.close()
    page_soup = soup(page_html, "html.parser")
    page_con = page_soup.find("div", {"class": "_2MImiq _1Qnn1K"})
    pages = int(page_con.span.text[10:].replace(',', ''))

    ur_list = []
    print(pages)
    if pages > 10:
        pages = 10

    for i in range(1, pages+1):
        str1 = url + "&page=" + str(i)
        ur_list.append(str1)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(scrap3, ur_list)

    cloud = WordCloud().generate(rev)
    cloud.to_file('static/MyProject/images/wc.png')
    return render(request, 'MyProject/wordcloudd.html')
