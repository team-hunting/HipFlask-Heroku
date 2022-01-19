from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup as bs

app = Flask(__name__)

headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }

@app.route('/') # Equivalent to: app.add_url_rule('/', '', index)
def index():
    return render_template('comic.html')

@app.route('/urlsearch')
def urlsearch():
    return render_template('urlsearch.html')

@app.route('/api/comic/comicinfo', methods=['POST'])
def comicInfo():
    content_type = request.headers.get('Content-Type')

    if content_type == 'application/json':
        content = request.get_json()
        url = content['url']
        singleIssue = False
        if "?id=" in url:
            singleIssue = True
        comicTitle = getComicTitle(url, singleIssue)
        
        print(content)
        print(content['url'])

    return {"title": comicTitle, "singleissue": singleIssue}

@app.route('/api/comic/issueinfo', methods=['POST'])
def issueInfo():
    content_type = request.headers.get('Content-Type')

    # For testing purposes
    return {"title": "Sandman...Lucifer...Whatever", "issues":[[
    "Issue-1",
    "https://readcomiconline.li/Comic/Sandman-Presents-Lucifer/Issue-1?id=37194"
],[
    "Issue-2",
    "https://readcomiconline.li/Comic/Sandman-Presents-Lucifer/Issue-2?id=37196"
],[
    "Issue-3",
    "https://readcomiconline.li/Comic/Sandman-Presents-Lucifer/Issue-3?id=37198"
] ]}

    if content_type == 'application/json':
        content = request.get_json()
        print("CONTENT: " + str(content))
        url = content['url']
        title = getComicTitle(url)
        issueLinks = getLinksFromStartPage(url)
        print("STARTURL :   " + url)
        issues = [(getIssueName(issueLink, "/Comic/" + title), "https://readcomiconline.li" + issueLink) for issueLink in issueLinks]
        print(issues)
        
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
        #return scrapeImageLinksFromIssue(url, hq)
    
    # this only hits if the wrong type of request is sent
    return {"imageLinks":["https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Klaus_Barbie.jpg/176px-Klaus_Barbie.jpg","https://upload.wikimedia.org/wikipedia/commons/thumb/7/79/Hoodoo_Mountain.jpg/243px-Hoodoo_Mountain.jpg"]}

def getComicTitle(url, issue=False):
    prefix = "https://readcomiconline.li"
    startURL = prefix + "/Comic/"
    title = url.replace(startURL, "", 1)
    if title[-1] == "/":
        title = title[:-1]

    if "?id=" in url:
        issue = True
    if issue:
        # Add the issue number to the title
        titlePieces =   title.split("/")
        issueTitle = titlePieces[1].split("?")[0]
        title = titlePieces[0] + "-" + issueTitle

    return title

def getLinksFromStartPage(url):
    req = requests.get(url, headers)
    soup = bs(req.content, 'html.parser')

    links = soup.find_all('a')
    linkArrayRaw = []
    for link in links:
        if link.get('href') != None:
            linkArrayRaw.append(link.get('href'))

    linkArray = []
    for link in linkArrayRaw:
        if link.startswith('/Comic/'):
            linkArray.append(link)

    linkArray.reverse()

    return linkArray

def getIssueName(issueLink, startURL):
    # remove the start url, trim the leading /, and everything after the ?
    issueName = issueLink.replace(startURL, "", 1)[0:].split("?",1)[0]
    if issueName[0] == "/":
        issueName = issueName[1:]
    return issueName

def scrapeImageLinksFromIssue(url, lowres=True):
    req = requests.get(url, headers)
    soup = bs(req.content, 'html.parser')
    soup = soup.prettify()
    lines = soup.split("\n")
    imageLinks = []

    print(lines)

    for line in lines:
        if "https://2.bp.blogspot.com" in line:
            imageUrl = extractImageUrlFromText(line, lowres)
            imageLinks.append(imageUrl)

        # if checkForCaptcha(line):
        #     solveCaptcha(url)
        #     return scrapeImageLinksFromIssue(url, lowres)

    return {"imageLinks":imageLinks}

def extractImageUrlFromText(text, hq):
    # urlEnd = text.find("s1600")
    urlEnd = text.find(")")
    urlStart = text.find("https")
    output = text[urlStart:urlEnd-1]
    print("extracted image link: " + output)
    # verbose
    # print("extractImageUrlFromText output ", output)
    if hq:
        output = output.replace("s1600","s0")
    return output