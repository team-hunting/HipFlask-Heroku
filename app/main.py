from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/') # Equivalent to: app.add_url_rule('/', '', index)
def index():
    return "<h1>Welcome Friend</h1>"

@app.route('/comic')
def test():
    return render_template('comic.html')

@app.route('/api/comic/comicinfo', methods=['POST'])
def comicInfo():
    content_type = request.headers.get('Content-Type')
    print(content_type)

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

    if issue:
        # Add the issue number to the title
        titlePieces =   title.split("/")
        issueTitle = titlePieces[1].split("?")[0]
        title = titlePieces[0] + "-" + issueTitle

    return title