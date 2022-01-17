from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup as bs

app = Flask(__name__)

@app.route('/') # Equivalent to: app.add_url_rule('/', '', index)
def index():
    return render_template('comic.html')

@app.route('/comic')
def test():
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
        comicTitle = getComicTitle(url, singleIssue)
        
        print(content)
        print(content['url'])

    return {"title": comicTitle, "singleissue": singleIssue}


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

@app.route('/api/comic/issueinfo', methods=['POST'])
def issueInfo():
    content_type = request.headers.get('Content-Type')

    if content_type == 'application/json':
        content = request.get_json()
        print("CONTENT: " + str(content))
        url = content['url']
        title = getComicTitle(url)
        issueLinks = getLinksFromStartPage(url)
        print("STARTURL :   " + url)
        issues = [(getIssueName(issueLink, "/Comic/" + title), "https://readcomiconline.li" + issueLink) for issueLink in issueLinks]
        print(issues)
        
        #TODO: process the issue tuples using JS in comic.html
        return {"title": title, "issues": issues}

    else:
        return {}

def getLinksFromStartPage(url):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }

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