var async = require('async');
var express = require('express');
var router = express.Router();

var db = require('../private/db');

// Statically gather the language count on server start
var languages;
db.get_languages(function(err, langs) {
  // Make languages a sorted list by count
  var langArray = [];
  for (var lang in langs) {
    var langObj = {
      language: lang,
      count: langs[lang]
    };
    langArray.push(langObj);
  }
  var languagesCount = langArray.reduce(function(a,b) {
    return a + b.count;
  }, 0);

  for (var i in langArray) {
    var percent = langArray[i].count / languagesCount;
    var r = Math.round(percent * 255 * 99);
    var color ='rgb(' + r + ',45,34)';
    langArray[i].color = color;
  }

  langArray.sort(function(a, b) {
    return b.count - a.count;
  });
  languages = langArray;

});


/* GET home page. */
router.get('/', function(req, res, next) {
  var requestStart = +new Date;
  var query = req.query.q;

  // Send the queries to the db.
  // Remember that all the callbacks return the error object then the result!
  async.parallel({
    count_summary: function(cb) {
      db.count_summary(cb);
    },
    search: function(cb) {
      db.search(query, cb);
    }
  }, function(err, data) {
    // After doing all the queries in parallel, render the page!

    data.languages = languages;
    data.languagesAlphabetical = data.languages.slice().sort(function(a,b) {
      a = a.language.toLowerCase();
      b = b.language.toLowerCase();
      return (a > b) ? 1 : ((b > a) ? -1 : 0);
    });
    data.query = query; // may be undefined
    // console.log('Render /index.html with the following data:');
    // if (data.search.hits) {
    //   for (var i = 0; i < data.search.hits.length; ++i) {
    //     console.log(data.search.hits[i].implementations[0]);
    //   }
    // }
    var requestEnd = +new Date;
    var requestTime = requestEnd - requestStart;
    data.requestTime = requestTime / 1000;
    res.render('index', data);
  });
});

module.exports = router;
