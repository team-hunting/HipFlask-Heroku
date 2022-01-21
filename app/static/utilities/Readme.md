## Links to the relevent github repos:
- https://github.com/Stuk/jszip/blob/master/dist/jszip.js
- https://github.com/Stuk/jszip-utils/blob/master/dist/jszip-utils.js
- https://github.com/eligrey/FileSaver.js/blob/master/dist/FileSaver.js

## How to use:
In the HTML:
```
<div class="text-center" >
    <br/>
    <button class="btn btn-lg btn-warning" id="downloadimagesbutton">Download All Images</button>
</div>
```
<script type="text/javascript" src="{{ url_for('static', filename='utilities/jszip.js')}}"></script>
<script type="text/javascript" src="{{ url_for('static', filename='utilities/jsziputils.js')}}"></script>
<script type="text/javascript" src="{{ url_for('static', filename='utilities/filesaver.js')}}"></script>


In the JS: (Note: CORS may prevent this from working if the img is not on the same domain)

```
function urlToPromise(url) {
    return new Promise(function(resolve, reject) {
        JSZipUtils.getBinaryContent(url, function (err, data) {
            if(err) {
                reject(err);
            } else {
                resolve(data);
            }
        });
    });
    }
  
  
downloadimagesbutton.addEventListener('click', (e) => {

    let filename = "asda.jpg";
    let zip = new JSZip();
    zip.file(filename, urlToPromise("https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Klaus_Barbie.jpg/176px-Klaus_Barbie.jpg"), {binary:true});

    zip.generateAsync({type:"blob"})
        .then(function callback(blob) {

            // see FileSaver.js
            saveAs(blob, "example.zip");
        });
})
```