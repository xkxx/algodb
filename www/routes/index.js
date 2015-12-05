var async = require('async');
var express = require('express');
var router = express.Router();

var db = require('../private/db');

/* GET home page. */
router.get('/', function(req, res, next) {
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

    data.query = query; // may be undefined
    console.log('Render /index.html with the following data:');
    if (data.search.hits) {
      for (var i = 0; i < data.search.hits.length; ++i) {
        console.log(!!data.search.hits[i].implementations);
      }
    }
    res.render('index', data);
  });
});

module.exports = router;
