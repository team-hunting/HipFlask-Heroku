#!/usr/bin/env python3
import requests
import os
from bs4 import BeautifulSoup as bs
import shutil

headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }

def getComicTitle(url):
    prefix = "https://readcomiconline.li"
    startURL = prefix + "/Comic/"
    title = url.replace(startURL, "", 1)
    if title[-1] == "/":
        title = title[:-1]

    issue = False
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

def scrapeImageLinksFromIssue(url, hq=True):
    req = requests.get(url, headers)
    soup = bs(req.content, 'html.parser')
    soup = soup.prettify()
    lines = soup.split("\n")
    imageLinks = []
    # verbose
    # print(lines)

    for line in lines:
        if "https://2.bp.blogspot.com" in line:
            imageUrl = extractImageUrlFromText(line, hq)
            imageLinks.append(imageUrl)

        # if checkForCaptcha(line):
        #     solveCaptcha(url)
        #     return scrapeImageLinksFromIssue(url, lowres)

    return { "imageLinks" : imageLinks }

def extractImageUrlFromText(text, hq):
    # urlEnd = text.find("s1600")
    urlEnd = text.find(")")
    urlStart = text.find("https")
    output = text[urlStart:urlEnd-1]
    # verbose
    # print("extracted image link: " + output)
    # print("extractImageUrlFromText output ", output)
    if hq:
        output = output.replace("s1600","s0")
    return output

def saveImageFromUrl(url, numberOfImages, issueName, title, currentNumber):
    digits=len(str(numberOfImages))

    path = os.getcwd() + os.sep + title + os.sep + issueName + os.sep

    if not os.path.exists(path):
        os.makedirs(path)

    filename = path + str(currentNumber).rjust(digits,"0") + ".jpg"
    with open(filename, "wb") as f:
        f.write(requests.get(url).content)

    # pass the path back for usage with zip
    return path

def folderCBZPacker(path, comicTitle, issuename):
    zipName = comicTitle + "-" + issuename
    try:
        shutil.make_archive(zipName, 'zip', path)
    except:
        print("This zip file already exists")

    try:
        os.rename(zipName + ".zip", zipName + ".cbz")
    except:
        print("This cbz file already exists")

def processDatabaseImageLink(link, hq):
    if link[-4] == ".":
        return link
    
    if hq:
        link = link + "=s0"
        return link
    else:
        link = link + "=s1600"
        return link
        