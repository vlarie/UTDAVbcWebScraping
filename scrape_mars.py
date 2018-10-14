#######################################################
##############  BeautifulSoup Scraper  ###############
#####################################################

from splinter import Browser
from bs4 import BeautifulSoup
import requests
# Used for featured image
import re   
import shutil
# Used for Mars Facts
import pandas as pd



def init_browser():
    exec_path = {'executable_path': '/Users/vlari/chromedriver.exe'}
    return Browser("chrome", **exec_path, headless=False)

def scrape():
    browser = init_browser()
    mars = {}

    ##################################
    ##########  Mars News  ##########
    ################################

    news_Mars_url = "https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest"
    browser.visit(news_Mars_url)

    html = browser.html
    soup = BeautifulSoup(html, "html.parser")

    mars["news_title"] = soup.find("div", class_="content_title").get_text()
    mars["news_p"] = soup.find("div", class_="article_teaser_body").get_text()


    ##################################
    #####  Mars Featured Image  #####
    ################################

    img_Mars_BaseUrl = "https://www.jpl.nasa.gov"
    img_Mars_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(img_Mars_url)

    style = soup.find('article')['style']
    urls = re.findall('url\((.*?)\)', style)
    img_EndUrl = urls[0][1:-1]

    featured_image_url = img_Mars_BaseUrl + img_EndUrl

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

    mars["mars_weather"] = soup.find(string = re.compile("Sol"))


    ##################################
    ##########  Mars Facts  #########
    ################################

    facts_Mars_url = "https://space-facts.com/mars/"

    mars_table = pd.read_html(facts_Mars_url)
    Property = mars_table[0][0]
    new_col = [item[:-1] for item in Property]   

    mars_factDF = pd.DataFrame(data=mars_table[0][1])
    mars_factDF.columns = ["Value"]
    mars_factDF["Property"] = new_col
    mars_factDF.set_index("Property", inplace=True)
    mars_factDF.to_html('./templates/marsFactDF.html')


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
    urls = [hemis_Mars_BaseUrl + item.find("a", class_="itemLink product-item").get("href") for item in mars_hemis]

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
    marsLists = [titles, urls]

    mars["hemisphere_image_urls"] = listTOdict(marsKeys, marsLists)




    ##################################
    #######  Mars Mongo Dict  #######
    ################################

    return mars