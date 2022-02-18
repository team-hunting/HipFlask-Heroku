# [HipFlask](https://hip-flask.herokuapp.com/)

This repo automatically deploys to https://hip-flask.herokuapp.com/ <br/> 

## What makes this project interesting?
- Overview: This is a Flask app optimized for deployment on Heroku through the use of Gunicorn WSGI (Web Server Gateway Interface) HTTP Server and other Heroku settings as detailed below. This app uses Bootstrap 5.1 elements for the UI.  
- Vanilla JS with ZERO dependencies means UI updates occur up to 30x faster than they would using a framework such as React. (Sitewide)
- ComicScraping: Performs web scraping against the website readcomiconline.li. Multiple public API endpoints for retrieving metadata and content for any available comic media on the website. Preempts any request with a call to a MongoDb Atlas cluster where any previously scraped data (by any user) is persisted. This helps to prevent unneeded requests, and thus helps prevent triggering anti-bot protection on the target site. Any request which isn't found in the database is scraped, and then persisted for future access. Flask is set to use a custom json_encoder to allow MongoDb outputs to be parsed correctly.
- ComicScraping: Uses Requests library to read the source code for the target page. The target site attempts to use dynamically loaded content to make scraping more difficult, but I read the content links directly from inline JavaScript. Content links are manipulated on the fly according to UI elements the user sets, and allows for high or low quality images to be retrieved. Scraping happens on a timer to prevent anti-bot protections from being triggered.
- ComicScraping: Users are able to download all of the scraped media in the form of a CBZ (comic book zip). This is achieved using server side zipping. The client then parses a blob sent from the server, manipulates it, downloads it, and frees the memory used by the blob. This takes advantage of the fact that Heroku doesn't use a persistent filesystem, and any excess files on the server are wiped every time it spins back up. I managed to put together a collection of libraries for client side image zipping which can be found here: [https://github.com/team-hunting/JS-Utilities](https://github.com/team-hunting/JS-Utilities) . Unfortunately in this case, a CORS policy prevents me from taking advantage of this at the moment. (I'll get around it eventually).
- MagicSearch: A simple but effective curated list of content websites. When you enter your search terms into the box and select the categories of interest, the JS will generate a set of formatted URLs containing your parameters, allowing you to save a significant amount of time in your search for content. 
- PixelSort: Pixel sorting is an image manipulation technique popularized and possibly invented by the conceptual artist Kim Asendorf around 2010. For digital artists like myself, this was an amazing tool. At first, the only way to use these scripts was through the [Processing Application](https://processing.org/), which (at least in the mid 2010s) was only really accessible to technical users. My goal with this page is to build a UI for, and integrate a modified pixel sorting library in python, to make this tool accessible to anyone.
- PixelSorting: So far, the largest hurdles to overcome have all been client side. The user is able to upload an image file which is then dynamically scaled and displayed in a canvas object. The user is able to select from a number of options and settings, and then send the image to the server for manipulation. Through the use of ObjectURLs and DataURLs the manipulated image is persisted on the client side and can be re-manipulated. I also added a 'rotate image' button which was shockingly non-straightforward to implement, at least in vanilla JS. 

## PIXEL SORTING TODO:
- Build UI elements for:
- Char.length
- Angle
- External interval file + upload box
- Sorting function
- Mask
- 
- Add a loading icon that hovers over the canvas while you wait for sorting
- Hide 'options' sections initially and reveal them in an accordian, or with a button or something
- Get a better default image in the static folder
- Update canvas size in case of default image
- Add ability to revert to original image(?) Use context.save() and context.restore()
- Add async method to delete the sorted image from server after it gets served back to client

## GENERAL TODO:
- Make a homepage 
- Make a 404 page
- Catch all unmatched URLs and route to 404
- Add some Vanta.js because it's cool 
- Rework the file saving and sending in  main.py. Specifically, the downloadIssue() function - we should replace the usage of send_file with send_from_directory for greater security. In order to do this we may need to rework the saveImageFromUrl() function to save images into one of the folders that flask has access to, perhaps 'static'. Ideally we could replace this with purely client side code, but blogspot has a CORS policy preventing this currently. For more info see static/utilities/Readme.md
- Set up a CORS proxy we can use to snag the blogspot images using fetch, then we can zip them client side
- Build more cool pages!!!


## Dev Info:

To develop Flask apps more effectively, turn on Debug/Development mode. <br/>
Run the command: ```export FLASK_ENV=development```, then use "flask run" in the same directory as wsgi.py (or just run wsgi.py). Because our entry point is named "wsgi.py" (this is a special name in flask) we don't need to set the FLASK_APP environment variable. "app.py" works as well. <br/>
This enables hot reloading and a traceback console in the browser.

Windows Powershell: ```$env:FLASK_ENV = "development"```  <br/>
Windows Git Bash:   ```export FLASK_ENV=development```    <br/>
Windows CMD:        ```set FLASK_ENV=development```       <br/>
Linux/etc:          ```export FLASK_ENV=development```    <br/>

Please note that you will need to update requirements.txt with any new requirements for Heroku.<br/>

If you run the app without development mode on, the WSGI server gives off a warning saying "WARNING: This is a development server. Do not use it in a production deployment." On Heroku we wrap the app with Gunicorn to support concurrency. This is controlled with the Procfile.<br/>

On Heroku WEB_CONCURRENCY config variable is set to 3 as per https://devcenter.heroku.com/articles/python-gunicorn <br/>

You will need to set a ```MONGODB_URI``` environment variable to connect to the DB. The value (for this specific deployment) can be found in the heroku settings if you have access. <br/>

## Notes:

HTML Escaping / Sanitizing inputs: <br/>
```
from markupsafe import escape
... return f"Hello, {escape(name)}!"
```

Templates rendered with Jinja will escape user values automatically. <br/>

Note: HTTP response 304 is for "Redirection to a previously cached result". <br/>

Flask quickstart: https://flask.palletsprojects.com/en/2.0.x/quickstart/ <br/>

Bootstrap components: https://getbootstrap.com/docs/5.0/customize/components/ <br/> 

Client Side zip & download functionality is contained under static/utilities/zip <br/>
