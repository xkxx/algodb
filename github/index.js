var request = require('request');
var atob = require('atob');

/**
 * Gets an api url string given a GitHub user and repo.
 */
function getURL(user, repo) {
  return 'https://api.github.com/repos/' + user + '/' + repo + '/readme';
}

function getReadmeData(cb) {
  var url = getURL('grant', 'talks');
  var options = {
    url: url,
    headers: {
      'User-Agent': 'request'
    }
  };
  request(options, function (error, response, body) {
    if (!error && response.statusCode == 200) {
      var json = JSON.parse(body)
      cb(json);
    }
  });
}

/**
 * Processes the GitHub API data
 */
function processReadmeData() {
  getReadmeData(function(data) {
    var readme = atob(data.content);
    console.log(readme);
  });
}

processReadmeData();

