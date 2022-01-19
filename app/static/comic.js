let infobutton = document.getElementById("infobutton");
let urlbox = document.getElementById("comicurl");
let urldisplay = document.getElementById("urldisplay");
let titledisplay = document.getElementById("titledisplay");
let singleissuedisplay = document.getElementById("singleissuedisplay");

infobutton.addEventListener('click', (e) => {
    let body = "https://readcomiconline.li/Comic/Sandman-Presents-Lucifer";

    if (urlbox.value == "") {
      console.log("You need to enter a URL... Selecting default")
      body = {"url": "https://readcomiconline.li/Comic/Sandman-Presents-Lucifer"};
    }
    else {
      body = {"url": urlbox.value};
    } 

    let requestOptions = {
        body: JSON.stringify(body),
        headers: {
            "Content-Type": "application/json"
        },
        method: "POST"
    }

    fetch(url, requestOptions).then(
        function(response) {
            return response.json();
    }).then(function(result) {
        urldisplay.value = body['url']
        titledisplay.value = result['title']
        singleissuedisplay.value = result['singleissue'] ? "Yes" : "No"
    }).catch(function(err) {
        console.log(err);
    });
})


let issuebutton = document.getElementById("getissuebutton");

let allImageLinks = {"links":[]};

issuebutton.addEventListener('click', (e) => {

  let displayImagesOnPage = document.getElementById('displayimages').checked;

  let urlval = urlbox.value == "" ? "https://readcomiconline.li/Comic/Sandman-Presents-Lucifer" : urlbox.value
  let body = {
    "url": urlval
  };

  console.log(body)

  let requestOptions = {
      body: JSON.stringify(body),
      headers: {
          "Content-Type": "application/json"
      },
      method: "POST"
  }

  fetch(issueUrl, requestOptions).then(
      function(response) {
        return response.json();
  }).then(async function(result) {
 
      console.log("Number of issues: ", result['issues'].length)
      console.log("Issues: ", result['issues'])
    
      // Display a warning that issues may take a while to download
      createDownloadIssueWarning()

      for (let i = 0; result['issues'].length > i; i++) {

        //TODO: create a loading icon while we wait for the next scrape to start

        issueLink = result['issues'][i][1]
        issueTitle = result['issues'][i][0]

        console.log(`Beginning scrape of ${issueTitle} at ${issueLink}`)

        // Display the 'Beginning to scrape issue x' text
        let info_section = document.createElement('div')
        info_section.setAttribute('id',`${result['title']}_${i}`);
        info_section.innerHTML = `Beginning scrape of ${issueTitle} at ${issueLink}`
        document.getElementById("comicdiv").appendChild(info_section);

        // Send issuelink to the api
        await getIssueHtml(issueLink).then(function(response) {

          let imglinks = response['imageLinks']
          
          // Global
          allImageLinks['links'].push(imglinks)

          // TODO: delete loading icon

          // Create an "Issue Download" button
          createDownloadIssueButton(i, issueTitle);

          // Optionally display the images on page
          if (displayImagesOnPage) {
            for (let i = 0; i < imglinks.length; i++) {
              displayImage(imglinks[i])
            }
          }
          
        }) 

        console.log("Sleeping for 15 seconds...");

        // SLEEP FOR 15 seconds before iterating again
        await new Promise(r => setTimeout(r, 15000));
      }

  }).catch(function(err) {
      console.log(err);
  });

})

function displayImage(imageUrl) {
  // TODO: stick images inside divs that resize based on viewport dimensions
  let image_section = document.createElement('div')
  let image_link = document.createElement('img')
  image_link.src = imageUrl
  image_section.appendChild(image_link)
  document.getElementById("comicdiv").appendChild(image_section);
}

async function getIssueHtml(issueLink) {

  let hqimages = document.getElementById('hqimages').checked;

  let requestOptions = {
        body: JSON.stringify({"issueLink":issueLink,"hq":hqimages}),
        headers: {
            "Content-Type": "application/json"
        },
        method: "POST"
    }

  let imageLinks = await fetch(issueImagesUrl, requestOptions).then(
        function(response) {
            return response.json();
  }).catch(function(err) {
      console.log(err);
  });

  console.log("imagelinks returned ", imageLinks)
  return imageLinks
} 

// Dev button for displaying Image links
// let showlinksbutton = document.getElementById("printimglinks");
// showlinksbutton.addEventListener('click', (e) => {
//   console.log("allImageLinks ", allImageLinks)
// })

function createDownloadIssueButton(issueNumber, issueTitle) {
  const button = document.createElement('button');
  const br = document.createElement('br');
  let numImages = allImageLinks['links'][issueNumber].length;
  let warning = numImages > 40 ? "- WARNING - LONG" : "";
  button.innerHTML = `Download ${issueTitle} : ${numImages} images ${warning}`;
  button.onclick = () => {downloadIssue(issueNumber, issueTitle)}
  document.getElementById("scrapedIssues").appendChild(button);
  document.getElementById("scrapedIssues").appendChild(br);
}

function createDownloadIssueWarning() {
    const warning = document.createElement('h');
    let br = document.createElement('br');

    warning.innerHTML = 
    "After clicking a download button, be aware that it may take up to a minute \
    before displaying the 'save as' box. Unfortunately, I think Heroku will cause \
    a request to time out if it hasn't responded in 30 seconds. \
    Extremely long issues, and using the High Quality switch may not work for this reason. \
    If this is happening to you, try using the switch to 'display images on this page' \
    and then save the entire page once they're done displaying. \
    You will have to pack the images into a zip file manually in this scenario. \
    If this solution doesn't work for you, feel free to donate so that I can afford a better hosting service. \
    If you're both desperate and poor, you can use our python script directly."

    document.getElementById("scrapedIssues").appendChild(br);
    br = document.createElement('br');
    document.getElementById("scrapedIssues").appendChild(warning);

    let a = document.createElement('a');
    a.innerHTML = "Clone it from: https://github.com/team-hunting/ComicDownloader";
    a.setAttribute('href',"https://github.com/team-hunting/ComicDownloader");
    
    document.getElementById("scrapedIssues").appendChild(br);
    document.getElementById("scrapedIssues").appendChild(a);
    br = document.createElement('br');
    document.getElementById("scrapedIssues").appendChild(br);
    br = document.createElement('br');
    document.getElementById("scrapedIssues").appendChild(br);
  }

function downloadIssue(issueNumber, issueTitle) {
  
  let links = allImageLinks['links'][issueNumber]; // this is an array of strings
  let title = getComicTitle(issueTitle);
  console.log("TITLE: " + title);

  let body = {"links":links,"title":title,"issueTitle":issueTitle}

  let requestOptions = {
        body: JSON.stringify(body),
        headers: {
            "Content-Type": "application/json"
        },
        method: "POST"
    }

    fetch(issueDownloadUrl, requestOptions).then(
        function(response) { 

          return response.blob();

    }).then(function(response) {

          const newBlob = new Blob([response]);
          const blobUrl = window.URL.createObjectURL(newBlob);

          const link = document.createElement('a');
          link.href = blobUrl;

          let filename;
          if (title != issueTitle) {
            filename = title + "-" + issueTitle + ".cbz"
          } else {
            filename = issueTitle + ".cbz"
          }
           
          link.setAttribute('download', `${filename}`);
          document.body.appendChild(link);
          link.click();
          link.parentNode.removeChild(link);

          // clean up Url
          window.URL.revokeObjectURL(blobUrl);

    }).catch(function(err) {
        console.log(err);
    });

}

function getComicTitleFromIssueLink(issuelink) {
  // https://readcomiconline.li/Comic/Sandman-Presents-Lucifer/Issue-3?id=37198
  let title = issuelink.replace("https://readcomiconline.li/Comic/", "");
  let titleArray = title.split("/");
  title = titleArray[0];
  console.log("TITLE DETECTED: " + title);
  return title;
}

function getComicTitle(issueTitle) {
  let title = urlbox.value.replace("https://readcomiconline.li/Comic/", "");
  // Default title
  if (title == "") {title = "Sandman-Presents-Lucifer"}

  if (title.slice(-1) === "/") {
    return title.slice(0,title.length -1)
  }

  if (title.includes("?id")) {
    return issueTitle
  }
    return title
  
}