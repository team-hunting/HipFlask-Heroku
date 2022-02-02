#!/usr/bin/env python3
from flask import Flask, render_template, request, send_from_directory, send_file
import os
from .comicscraping import *
from pymongo import MongoClient
from bson.json_util import ObjectId
import json
import random

# For MongoDB BSON objects
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super(MyEncoder, self).default(obj)

mongo = os.getenv('MONGODB_URI').replace("\"", "")
client = MongoClient(mongo)
db=client.comics

# Edit this to turn on dummy data
app_test = False

app = Flask(__name__)
app.json_encoder = MyEncoder


#TODO: Build simple page for pixel allowing user to upload image
# refactor pixelsorting code to take in arguments from user

#Pixelsorting
from PIL import Image
from pixelsort import pixelsort
from pixelsort.util import id_generator

@app.route('/pixelsort')
def pixel():
    return render_template('pixel.html')

@app.route('/api/pixel/sort', methods=['POST'])
def sortpixels():
    image_filename = id_generator() + str(random.randint(0,100000)) + ".png"
    image_path = os.getcwd() + os.sep + image_filename

    print(image_filename)
    print(image_path)

    print()
    print("PRINTING DATA")
    print(request.values)
    # Both work
    print(request.form['intervalfunction'])
    print(request.values['intervalfunction'])
    print()

    # intervalfunction = request.form['intervalfunction']
    # print(intervalfunction)


    file = request.files['image']
    # print("FILENAME: ", request.files['image'].filename)
    if request.files['image'].filename == "":
        print("No file detected")
        return send_from_directory('static', "default.jpg")

    img = Image.open(file)

    print(img.size) 

    pixelsort(img).save(image_path)

    return send_file(image_path, attachment_filename="sorted.png")


# TODO: Make a home page
@app.route('/') # Equivalent to: app.add_url_rule('/', '', index)
def index():
    return render_template('comic.html')

@app.route('/urlsearch')
def urlsearch():
    return render_template('urlsearch.html')

@app.route('/comicdownload')
def comic():
    return render_template('comic.html')

@app.route('/api/comic/comicinfo', methods=['POST'])
def comicInfo():
    content_type = request.headers.get('Content-Type')

    if content_type == 'application/json':
        content = request.get_json()
        url = content['url']
        singleIssue = False
        if "?id=" in url:
            singleIssue = True
        comicTitle = getComicTitle(url)
        
        print(content)
        print(content['url'])

    return {"title": comicTitle, "singleissue": singleIssue}

@app.route('/api/comic/issueinfo', methods=['POST'])
def issueInfo():
    content_type = request.headers.get('Content-Type')

    # For testing purposes
    if app_test:
        output = test_output
        outputdb = test_outputdb
        
        existingissue = db.series.find_one({"title":outputdb["title"]})

        if existingissue is None:
            print("Inserting Comic into DB")
            db.series.insert_one(outputdb)
        
        return output

    if content_type == 'application/json':
        content = request.get_json()
        print("CONTENT: " + str(content))
        url = content['url']

        issue = False
        if "?id=" in url:
            issue = True

        title = getComicTitle(url)
        
        existingissue = db.series.find_one({"title":title})

        if (existingissue is not None):
            print("comic found in DB")
            if issue:
                issues = [(existingissue["title"], existingissue["issues"][0]["url"])] 
            else:
                issues = [(issue["title"], issue["url"]) for issue in existingissue["issues"]] 
            return {"title": title, "issues": issues}          

        if issue:
            issueLinks = [url]
        else:
            issueLinks = getLinksFromStartPage(url)

        if issue:
            issuesdb = [{"title": title, "url": url}]
            issues = [(title, url)]
        else:
            issuesdb = [{"title": getIssueName(issueLink, "/Comic/" + title), "url": "https://readcomiconline.li" + issueLink} for issueLink in issueLinks]
            issues = [(getIssueName(issueLink, "/Comic/" + title), "https://readcomiconline.li" + issueLink) for issueLink in issueLinks]
                
        print(f"Inserting {title} into DB")
        db.series.insert_one({"title": title, "issues": issuesdb})
        return {"title": title, "issues": issues}

    else:
        return {}

@app.route('/api/comic/scrapeissue', methods=['POST'])
def scrapeIssue():
    content_type = request.headers.get('Content-Type')

    if content_type == 'application/json':
        content = request.get_json()
        print("CONTENT: " + str(content))
        url = content['issueLink']
        print("URL: " + url)
        if "&readType=1" not in url:
            print("Adding '&readType=1' to url")
            url = url + "&readType=1"
        hq = content['hq']
        print("HQ: " + str(hq))
        print("TYPEOF HQ: ", type(hq))

        print("URL: " + url)
        if not app_test:
            dburl = url.split("&read")[0]
            print("DB URL: " + dburl)
            existingimages = db.images.find_one({"url":dburl})

            if existingimages is not None:
                print("Image links found in DB")
                # Process url strings to add =s0 , =s1600, or nothing
                processedImageLinks = [processDatabaseImageLink(imageLink, hq) for imageLink in existingimages["imageLinks"]]
                return {"imageLinks": processedImageLinks, "fromDb": True }

            imgLinks = scrapeImageLinksFromIssue(url, hq)
            print("Inserting Img Links")
            db.images.insert_one({"url": url.split("&read")[0], "imageLinks": [link.split("=")[0] for link in imgLinks["imageLinks"]]})

            return {"imageLinks": imgLinks["imageLinks"], "fromDb": False}

    # this only hits if the wrong type of request is sent
    # Dummy data from wikipedia
    # return {"imageLinks":["https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Klaus_Barbie.jpg/176px-Klaus_Barbie.jpg","https://upload.wikimedia.org/wikipedia/commons/thumb/7/79/Hoodoo_Mountain.jpg/243px-Hoodoo_Mountain.jpg"]}
    # Real data for Lucifer (blogspot)
    imgLinks = {"imageLinks":['https://2.bp.blogspot.com/QGtDCkEEAplwbN1aD56FLTS3xSKgWh5fanmE9gePQWCB9Tk3uk5tchuli3FeDOFr7WfkC92z_p0=s0', 'https://2.bp.blogspot.com/yjSWP9jjzvV8e-DNKX1U0ftunYprLELUe5X0dIaHOmYK2jTpjCShMTFMbrQwNfMWI_jUrlq4nkQ=s0', 'https://2.bp.blogspot.com/d200xZpFAm85njb7Jaiqz1REK0GfSyc09NHEgSCG0FIrIEipXOv7pADiMKoSDU109Rjj7lELBqs=s0', 'https://2.bp.blogspot.com/cpBljpXugNlmYMpR1V8nkTSdy5iKvgTUBvn5hJdBBAhBCI8t6Bsd06mHBfWdkygdpYP1xCOulLA=s0', 'https://2.bp.blogspot.com/zEpK66FrKHP-5_Lp0bYTgVvac3uEHqZkMmcNkr8a5ifQHPgjHU8QtMLD-LG1xYxwcIqg94Oss_Q=s0', 'https://2.bp.blogspot.com/gJfYll9_oaG2USHNGyJN1Nao785FPpmhBD3b-PYFNI69j_HjJHt8otUTnIU2yrnyZiDb5nUfSxI=s0', 'https://2.bp.blogspot.com/4xcLy7WIZZGPKeKVDR6Y-gpgVnTM3SZqWD8ooRHjgKnkb4uj2M5Afz5FWRo60awWzUw4GV6U8oo=s0', 'https://2.bp.blogspot.com/g9y-8Y0_6dnMv7PIVbWBHq643Wy_gXh4VyMBUFF1eeK9j83ZU9nU1evQBiJf3Lx_mqDyRXLx7Z4=s0', 'https://2.bp.blogspot.com/p2FDlR242bME1Jg2KS8NEln5JkEIin2W2--aZJmfuiLcYrLdX7eWURtvedcLR_09CiUJ0Ua7oPI=s0', 'https://2.bp.blogspot.com/_ic9RAxZHSVpJy1bWbnjNtR_JWuAL16TJzSBlaknRMJl4RZiePOZFcFmHSCte5LxqIlXyGu3rj8=s0', 'https://2.bp.blogspot.com/gefRwe8qKCJTKCZIiGrqF___mbJxNzNW3LkOtE5IvaYJV8g4nZC6fid9kjoGfksGLetxIjdhZ6c=s0', 'https://2.bp.blogspot.com/uBBsFDJlV4RRgQFtOCCDoEerUq8z9vbXOwfY3Np9pAGCwC844k1HpC35u0Ihg__Sy3zV442oS44=s0', 'https://2.bp.blogspot.com/WRHm4mwy87DxA2H5IZnkFL-ScJxlGxBarb9qL6Ug5-S9HAMDkCYm-Y_Ll1LQ4If_vwXza12fif8=s0', 'https://2.bp.blogspot.com/TFH1zAzudxc9ivVcmTs_zfQwiWbxUY_gLO_exqfUCJjPg4W5eUJfiHns8Iy3wGYCNnEJBFQSHNs=s0', 'https://2.bp.blogspot.com/pVB5xhrN6JLPTQZLJi3a3lAgYVIjItQtg8-U_ZAZDr112ek8ORGl-CDVMtfNS9LyH98uuh1_S2s=s0', 'https://2.bp.blogspot.com/d1NYTf30CQS12HtWgoFFFywJvJDowDb83sHkkgDApmgDO2nUDmOcpSRiDBDzt6KQq72nYgiqGJk=s0', 'https://2.bp.blogspot.com/5s-b3pJnwImygJOs1N0mNYDUwu43Ywar_K4qNOOppuq6IXUVlRvtde7lzeBGbUroHwq5PGNRibA=s0', 'https://2.bp.blogspot.com/IdEyrmI94krFY5d33Muxl9I0g7Hz2bn5SDYQtKga1a-zoPjrdWKwWqbutT8XshUyvGAdoREnjzs=s0', 'https://2.bp.blogspot.com/zyJ2WZsteeOxzdLS0fWzHMw4t5PrE8oG2raPl9_zAqle2GYsGra6BwJ2CWjM3V-1G06Vp6V4ki0=s0', 'https://2.bp.blogspot.com/-u51BDju5BFpZAWyq3xnamp6YyEPTOqKK3XlkyfUz3ojCzk89dQVlez9SDlrmIgUaWzSO9pt8Zg=s0', 'https://2.bp.blogspot.com/4aMSa8mRFRioIjYjh90nPyrsGxrli3QcJ62zJh4fQKWpOa_AQf--c3KLMHxkFLHK184mpQs7yDM=s0', 'https://2.bp.blogspot.com/mWIeN7Qd4XDefZIQa-Le5g0CssBmR-YUIL4ZODY-kw_79Je01nHCsDKLv39iUdhyUn8qmuQsH8o=s0', 'https://2.bp.blogspot.com/U89XpO9V8telVAn82dv7HIV-AVHOrYY9HraWqlY-TlaPL5XI1DI5MV_2M4GlAtk5b9tM4zZqWxs=s0', 'https://2.bp.blogspot.com/7omHiWgC76ALRZOzMb9Okl1NkAMV6KbTURPZ3aXkuJolU81O6GgrtYImdih5oDvGmpS8o0Sa0J0=s0']}
    return {"imageLinks": imgLinks["imageLinks"], "fromDb": False}

@app.route('/api/comic/downloadissue', methods=['POST'])
def downloadIssue():
    content_type = request.headers.get('Content-Type')

    if content_type == 'application/json':
        content = request.get_json()
        print("CONTENT: " + str(content))
        imageLinks = content['links']
        print("IMAGE LINKS: " + str(imageLinks))
        numImages = len(imageLinks)
        title = content['title']
        issueTitle = content['issueTitle']
        for i in range(len(imageLinks)):
            link = imageLinks[i]
            path = saveImageFromUrl(link, numImages, issueTitle, title, i)

        folderCBZPacker(path, title, issueTitle)
        cbzFile = title + "-" + issueTitle + ".cbz"
        cbzFilePath = os.getcwd() + os.sep + cbzFile

        try:
            print("CURRENT DIRECTORY: ", os.getcwd())
            print("CBZ path: ", cbzFilePath)
            # TODO: use send_from_directory and have the file saved into the 'static' folder (or a new folder, whatever)
            return send_file(cbzFilePath, attachment_filename=cbzFile)
        except:
            print("Something went wrong")
            return {}

    return {}


# TODO: Delete this
test_output = {"title": "Sandman...Lucifer...Whatever", "issues":
        [
            [
        "Issue-1",
        "https://readcomiconline.li/Comic/Sandman-Presents-Lucifer/Issue-1?id=37194"
            ],
            [
        "Issue-2",
        "https://readcomiconline.li/Comic/Sandman-Presents-Lucifer/Issue-2?id=37196"
            ],
            [
        "Issue-3",
        "https://readcomiconline.li/Comic/Sandman-Presents-Lucifer/Issue-3?id=37198"
            ] 
        ]}

test_outputdb = {
            "title": "Example-Comic-Title",
            "issues": [
                {
                    "title": "Issue-1", 
                    "url": "https://readcomiconline.li/Comic/Sandman-Presents-Lucifer/Issue-1?id=37194"
                },
                {
                    "title": "Issue-2",
                    "url": "https://readcomiconline.li/Comic/Sandman-Presents-Lucifer/Issue-2?id=37196"
                },
                {
                    "title": "Issue-3",
                    "url": "https://readcomiconline.li/Comic/Sandman-Presents-Lucifer/Issue-3?id=37198"
                }
            ]
        }
