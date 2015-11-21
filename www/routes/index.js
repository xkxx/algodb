var express = require('express');
var router = express.Router();

/* GET home page. */
router.get('/', function(req, res, next) {
  var query = req.query.q;
  var results = [];

  var data = {
    query: query,
    results: results
  };

  res.render('index', data);
});

module.exports = router;
