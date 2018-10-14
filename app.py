#######################################################
################  Flask Application  #################
#####################################################

from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars

app = Flask(__name__)

# Establish MongoDB connection
mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_app")


@app.route("/")
def home():
    print("Server received request for 'Home' page")
    listings = mongo.db.listings.find_one()
    return render_template("index.html", listings=listings)

@app.route("/scrape")
def scraper():
    print("Server received request to scrape Mars")
    listings = mongo.db.listings
    listings_data = scrape_mars.scrape()
    listings.update({}, listings_data, upsert=True)
    return redirect("/", code=302)


if __name__ == "__main__":
    app.run(debug=True)