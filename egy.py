import requests
from bs4 import BeautifulSoup
import imdb
from pymongo import MongoClient
import arabic_bdr_pro
from threading import Thread
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
a = arabic_bdr_pro() #arabic library
# Load environment variables from .env file
import os
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv('.env')
api = os.environ.get("CONNECTION_STRING")
authapi = os.environ.get("NEW_CONNECTION_STRING")
mongo = os.environ.get("MONGO_CONNECTION_STRING")
print(api)
print(authapi)
print(mongo)
cluster = MongoClient(mongo)
db = cluster["Ananasa"] #database name
chromedriver = "ananasa\\chromedriver.exe"
os.environ["webdriver.chrome.driver"] = chromedriver
driver = webdriver.Chrome(chromedriver)
option = webdriver.ChromeOptions()
option.chrome_options.add_argument("--headless")
option.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36")
browser = webdriver.Chrome(executable_path='chromedriver.exe',options=option)

def UniqueInsert(collection, list_, index):
    if not inmongo(collection, list_, index):
        try:
            collection.insert_one(list_)
            print(f"inserted {list_}")
        except Exception as e:
            print(e)
            collection = db[list_["Series"]]
            UniqueInsert(collection, list_)
        return True
    return False


def inmongo(collection, list_, index):
    try:
        search = collection.find_one({index: list_[index]})
    except:
        return False
    if search is not None:
        print(f"found {search}")
        return True
    return False

#r = requests.get(url) #request to get the page
#print(f"Nyaa {r.stauts_code}") #print the status code
def findVideoLink(txt):
    txt=str(txt) #convert to string
    x=txt.find('http') #check if the link starts with http
    y=txt.find('mp4') #check if the link ends with mp4
    z=txt.find('m3u8') #if it does not end with mp4 then it must end with m3u8
    n=txt.find('mkv') #if it does not end with mp4 then it must end with m3u8
    g = txt.find('avi')
    b = txt.find('flv')
    k=txt.find('webm')
    l=txt.find('mov')
    q=txt.find('wmv')
    exe=[y,z,n,g,b,k,l,q]
    temp = [i for i in exe if (i!=-1)]
    y=min(temp) #find the minimum value
    return txt[x:y+3] #find the mp4 link


def findmp4(link): #function to get the mp4 link
    r = requests.get(link)
    soup = BeautifulSoup(r.content, 'html.parser')
    soup1=soup.find_all("script") #remove the script tag`
    newsoup=soup1[7]
    link=findVideoLink(newsoup)
    print(link)
    return link


def englishonly(txt): #function to get the english only title
    x = ''.join((y for y in txt if not y.isdigit()))
    x="".join((x[:0],"###",x[20:]))
    x = x.split("%")
    y = max(x, key=len)
    return y.replace("-"," ")


def egyFilm(link):
    try:
        r = requests.get(link)
        print(f"EgY Resopnse {r.status_code}")
        soup = BeautifulSoup(r.content, 'html.parser')
        link=soup.select('.code > iframe')
        link=str(link)
        src=link.find('data-src=')
        endsrc = link.find('frameborder')
        link=link[src+10:endsrc-2]
        print(link)
        if link.find("vadbam.net") == -1:
            return
        link=findmp4(link)
        return link
    except Exception as e:
            print(e)    

def changePagelink(url,num):        #function to change the page number
    print(url)
    url2 = url.replace(f"p={num}", f"p={str(num + 1)}")
    print(url2)
    r=requests.get(url2)
    try:
        print(f"Nyaa {r.status_code}")
    except Exception as e:
        print(f"No more nyaa pages {e}")
        return None
    return url2


def MagnetLink(url):                #function to get the magnet link


    try:
        for i in url: 
            r = requests.get(i)
            print(r)
            soup = BeautifulSoup(r.content, 'html.parser')
            magnet_url = soup.findAll('div',attrs={'class': 'panel-footer clearfix'}) #get the magnet link
            for div in magnet_url:
                Magnet=div.find('a')['href']
                print(Magnet)
                links = soup.find('a', attrs={'href': lambda L: L and L.startswith('magnet')}).get('href')
                print(links)
                Magnetappend(e, soup, links, Magnet)
    except Exception as e:
        print(f"No more nyaa pages Or connection error {e}")


# TODO Rename this here and in `MagnetLink`
def Magnetappend(e, soup, links, Magnet):
    print(e)
    title=soup.find('title').text
    print(title)
    series=animeTitleInImdb(title)
    AnimeDictTemp = {"Series":series,"Nyaa":True,"title": title,
    "url": links , "Download": f"https://nyaa.si{Magnet}"} #dictionary to store the data

    if UniqueInsert(series,AnimeDictTemp,"title"):     #calling the function to insert the data
            print("done updating")
    else:
            print("Already in the database")
    


def ViewNyaaLinks():                             #function to get the links of the anime
    # sourcery skip: hoist-statement-from-loop
    Nyaaurl = [ "https://nyaa.si/?f=0&c=1_4&q=&p=" , "https://nyaa.si/?p=", 
    "https://nyaa.si/?f=0&c=1_3&q=&p=","https://wnyaa.si/?f=0&c=1_2&q=&p=" ] #url of the page
    try:
        for i in Nyaaurl:
            while True:
                num=1 # page counter
                url=changePagelink(i,num)
                if url is None:
                    break
                r = requests.get(url)
                print(r)
                if(r.status_code!=200):
                        return print(f"No more nyaa pages Or connection error \n {r.status_code}")
                soup = BeautifulSoup(r.content, 'html.parser')
                tbody = soup.find('tbody')
                trs = tbody.find_all('tr')
                urlView1=[]
                for i, tr in enumerate(trs):
                    td_colspan2 = tr.find('td', {'colspan': '2'})
                    a_tag = td_colspan2.find('a')
                    href = a_tag['href']
                    urlView1.append(f"https://nyaa.si{href}")
                    print(urlView1[i])
                return MagnetLink(urlView1)
    except Exception as e:
        print(f"No more nyaa pages Or connection error \n {e}")

def animeTitleInImdb(name):
    # sourcery skip: merge-assign-and-aug-assign, move-assign
    try:
        animeObj = imdb.Cinemagoer()
        anime = animeObj.search_episode(name)
        animeid = anime[0].getID()
        print(animeid)
        title= animeObj.get_movie(animeid)
        tvseriesfinder = imdbfinder(animeid)
        if(tvseriesfinder.__len__()>2):
            for eposide in tvseriesfinder:
                print(eposide)
                season=0
                if("Season" in eposide):
                    season+=1
                dicti={title:f"S{season}+{eposide}","imdbID":animeid}
                UniqueInsert(title,dicti,eposide)
        print(title)
        return title
    except:
        return englishonly(name)

def imdbfinder(id):
    ia = imdb.IMDb()
    series = ia.get_movie(id)
    ia.update(series, 'episodes')
    episodes = series.data['episodes']
    print(series)
    listseries=[]
    for i in episodes.keys():
        
        # printing season number
        print(f"Season {str(i)}")
        listseries.append(f"Season {str(i)}")
        # traversing season i
        for j in episodes[i]:
            
            # getting title of episode
            title = episodes[i][j]['title']
            # printing title
            print(f" Ep{str(j)} : {title}")
            listseries.append(f"Ep {str(j) + title}")

    return listseries

def imdblink(title):
    url=f"https://www.google.com/search?q=imdb+{title}&btnI=%D8%B6%D8%B1%D8%A8%D8%A9+%D8%AD%D8%B8&hl=ar&sxsrf=APwXEde3EZWSKuvpYjqXA-GlNKgouzUf1Q%3A1682453066089&source=hp&ei=SjJIZMOIA8ymkdUPuJ2UqA0&iflsig=AOEireoAAAAAZEhAWmxKNF0zR834g5XgoNOrHd7MowVQ"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    link=soup.find('a', attrs={'href': lambda L: L and L.startswith('https://www.imdb.com/title/')}).get('href')      
    print(link)
    return link 

def get_links():
    href_links = []
    links = driver.find_elements(By.CSS_SELECTOR, "a")
    for link in links:
        href = link.get_attribute("href")
        if href and href not in href_links:
            href_links.append(href)
            print(href)
    return href_links

def selenium(dict):
    while True:
        i=0
        try:
            href=[]
            urls = list(dict.items())
            url=url[i][i]
            driver.get(url)
            i+=1
        except:
            print("No more egybest pages")
            while True:
                href=get_links()
                try:
                    element = driver.find_element(by=By.CSS_SELECTOR, value=".load-more")
                    element.click()
                    time.sleep(3)
                    print("clicked")
                except Exception as e:
                    print(e)
                    print("not clicked")
                    break
            title=urls[i]
            arabic_title=a.arabic(title)
            Series=englishonly(href[i])
            tempmovie=({"Series":Series,"egy":True,"title":arabic_title,"link":href[i]})
            if(UniqueInsert(Series,tempmovie,"title")):
                print("done")
            else:
                print("already in the database")
                return
           # egyFilm(href) retrive mp4 link
        driver.quit()


def egylinkfinder():#function to get the links of egybest 
    egytitle,egylink=egylinkscrapper()
    egy=dict(zip([egylink],[egytitle]))
    for i in egy:
        selenium(i)
        print("**************")

def egylinkscrapper():
    egylinks=[]
    titlename=[]
    print("Scraping The Fun")
    r = requests.get("https://egyibest.icu/")
    print(r.status_code)
    soup = BeautifulSoup(r.content, 'html.parser')
    link=soup.findAll('a', attrs={'href': lambda L: L and L.startswith('/egybest/')})
    for i in link:
        print(i['href'])
        titlename.append=i['href'].replace("/egybest/","")
        egylinks.append(f"https://egyibest.icu{i['href']}")
        
    return titlename,egylinks

def addBulk():
    
    return

while True:    
    try:                  
    
        Thread(target=addBulk()).start()
        print("Scraping The Fun")
        Thread(target=ViewNyaaLinks()).start()
        print("**************")
        Thread(target=egylinkfinder()).start()
        print("**************")
    except:   
        print("error")
    
