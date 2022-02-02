# [HipFlask](https://hip-flask.herokuapp.com/)

This repo automatically deploys to https://hip-flask.herokuapp.com/ <br/> 

## PIXEL SORTING TODO:
- Build UI elements for:
- Randomness
- Threshold lower and Threshold upper
- Char.length
- Angle
- External interval file + upload box
- Sorting function
- Mask
- Modify pixel sorting module to take these arguments (currently takes from cmd line)
- Get a better default image in the static folder
- Update canvas size in case of default image

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
