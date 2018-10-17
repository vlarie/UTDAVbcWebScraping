#######################################################
################  Flask Application  #################
#####################################################

from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars

app = Flask(__name__)

# Establish MongoDB connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_app"
mongo = PyMongo(app)


@app.route("/")
def home(): 
    print("Server received request for 'Home' page")
    mars = mongo.db.mars
    mars_data = scrape_mars.scrape()
    marsData = mongo.db.mars.find_one()
    return render_template("index.html", mars=marsData)

@app.route("/scrape")
def scraper():
    print("Server received request to 'scrape Mars'")
    mars = mongo.db.mars
    mars_data = scrape_mars.scrape()
    print(mars_data)
    mars.update({}, mars_data, upsert=True)
    return redirect("/", code=302)


if __name__ == "__main__":
    app.run(debug=True)