var request = require('request');


/**
 * Gets an api url string given a GitHub user and repo.
 */
function getURL(user, repo) {
  return 'http://api.github.com/repos/' + user + '/' + repo + '/readme';
}

function getReadmeData() {
  var url = getURL('grant', 'talks');
  request(url, function (error, response, body) {
    if (!error && response.statusCode == 200) {
      console.log(body); // Show the HTML for the Google homepage.
    }
  });
}

getReadmeData();
