var request = require('request');
var jsonfile = require('jsonfile');

// There can be a max of 5 terms
var terms = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];

var query = terms.join(',');
var url = 'http://www.google.com/trends/fetchComponent?q=' + query + '&cid=TIMESERIES_GRAPH_0&export=3';

// The results of the query is a list of the relative popularity of each query.

// Google trends hack
var google = {
  visualization: {
    Query: {
      setResponse: function(obj) {
        var file = 'data.json';
        jsonfile.writeFile(file, obj, function (err) {
          console.log('done');
        });
      }
    }
  }
};

request(url, function (error, response, body) {
  if (!error && response.statusCode == 200) {
    // eval!
    eval(body);
  }
});

