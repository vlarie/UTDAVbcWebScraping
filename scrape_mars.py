#######################################################
##############  BeautifulSoup Scraper  ###############
#####################################################

from splinter import Browser
from bs4 import BeautifulSoup
import requests
import time
# Used for featured image
import re   
import shutil
# Used for Mars Facts
import pandas as pd
import io



def init_browser():
    exec_path = {'executable_path': '/Users/vlari/chromedriver.exe'}
    return Browser("chrome", **exec_path, headless=True)

def scrape():
    browser = init_browser()
    mars = {}

    ##################################
    ##########  Mars News  ##########
    ################################

    news_Mars_BaseUrl = "https://mars.nasa.gov"
    news_Mars_url = "https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest"
    browser.visit(news_Mars_url)
    time.sleep(5)

    html = browser.html
    soup = BeautifulSoup(html, "html.parser")
    time.sleep(5)

    mars["news_title"] = soup.find("div", class_="content_title").get_text()
    news_url = soup.find("div", class_="content_title").find("a").get("href")
    mars["news_url"] = news_Mars_BaseUrl + news_url
    mars["news_p"] = soup.find("div", class_="article_teaser_body").get_text()
    news_img = soup.find("div", class_="list_image").find("img").get("src")
    mars["news_img"] = news_Mars_BaseUrl + news_img


    ##################################
    #####  Mars Featured Image  #####
    ################################

    img_Mars_BaseUrl = "https://www.jpl.nasa.gov"
    img_Mars_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(img_Mars_url)
    time.sleep(10)

    html = browser.html
    soup = BeautifulSoup(html, "html.parser")

    style = soup.find('article')['style']
    mars["feat_img_capt"] = soup.find('article').get("alt")
    time.sleep(5)
    urls = re.findall('url\((.*?)\)', style)
    img_EndUrl = urls[0][1:-1]
    featured_image_url = img_Mars_BaseUrl + img_EndUrl

    mars["featured_image_url"] = featured_image_url

    response = requests.get(featured_image_url, stream=True)
    with open('./static/images/mars_feat_img.png', 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)


    ##################################
    #########  Mars Weather  ########
    ################################

    twitWeather_Mars_url = "https://twitter.com/marswxreport?lang=en"
    browser.visit(twitWeather_Mars_url)

    html = browser.html
    soup = BeautifulSoup(html, "html.parser")

    mars["mars_weather"] = soup.find(string = re.compile("Sol")).split(", ")


    ##################################
    ##########  Mars Facts  #########
    ################################

    facts_Mars_url = "https://space-facts.com/mars/"

    mars_table = pd.read_html(facts_Mars_url, encoding="UTF-8")
    description = mars_table[0][0]
    new_col = [item[:-1] for item in description]   

    mars_factDF = pd.DataFrame(data=mars_table[0][1])
    mars_factDF.columns = ["Value"]
    mars_factDF["Description"] = new_col
    mars_factDF = mars_factDF[["Description", "Value"]]
    mars_factDF.to_html('./templates/marsFactDF.html', index=False)

    # Alter table to add Bootstrap styling using BeautifulSoup
    with open("./templates/marsFactDF.html") as infile:
        htmltxt = infile.read()
        soup = BeautifulSoup(htmltxt, "html")

    table = soup.table
    table["class"] = "table table-hover table-striped"
    table["id"] = "marsFacts"
    del table["border"]

    thead = soup.thead
    thead["class"] = "thead-dark"

    tr = soup.tr
    del tr["style"]

    # Save new file with html changes
    with open("./templates/marsFactDFsouped.html", "w") as outfile:
        outfile.write(str(soup.table))

    # Overwrite file to convert html to UTF-8 encoding
    with io.open("./templates/marsFactDFsouped.html",'r') as infile:
        text = infile.read()
    with io.open("./templates/marsFactDFsouped.html",'w',encoding='utf8') as outfile:
        outfile.write(text)


    ##################################
    #######  Mars Hemispheres  ######
    ################################

    hemis_Mars_BaseUrl = "https://astrogeology.usgs.gov"
    hemis_Mars_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(hemis_Mars_url)

    html = browser.html
    soup = BeautifulSoup(html, "html.parser")

    mars_hemis = soup.find("div", class_="collapsible results").find_all("div", class_="item")
    titles = [item.find("h3").get_text() for item in mars_hemis]
    # URLs returned are not the img src URL
    urls = [hemis_Mars_BaseUrl + item.find("a", class_="itemLink product-item").get("href") for item in mars_hemis]
    
    # This loop visits each URL found above to obtain the img src for each page
    img_urls = []
    for item in urls:
        browser.visit(item)
        html = browser.html
        soup = BeautifulSoup(html, "html.parser")
        browser.find_by_id('wide-image-toggle').first.click()
        img_url = soup.find("img", class_="wide-image").get("src")
        img_urls.append(hemis_Mars_BaseUrl + img_url)

    def listTOdict(keys, lists):
        if len(keys) != len(lists):
            print("Parameters must be equal in length")
            return []
        rows = len(lists[0])
        cols = len(keys)
        listed = []
        for r in range(rows):
            entry = {}    
            for c in range(cols):
                entry[keys[c]] = lists[c][r]
            listed.append(entry)
        return listed

    marsKeys = ["title", "url"]
    marsLists = [titles, img_urls]

    mars["hemisphere_image_urls"] = listTOdict(marsKeys, marsLists)




    ##################################
    #######  Mars Mongo Dict  #######
    ################################

    return mars