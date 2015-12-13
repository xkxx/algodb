var bluebird = require('bluebird');
var redis = require("redis"),
    r = bluebird.promisifyAll(redis.createClient());

var npmLibs = require('./get-desc');
var fs = bluebird.promisifyAll(require('fs'));

var main = function() {
  fs.readFileAsync('list.json', 'utf-8')
  .then(function(blob) {
    return JSON.parse(blob);
  })
  .each(function(pkg) {
    return r.saddAsync('pkgs', pkg);
  })
  .then(function() {
    console.info('all done');
    r.quit();
  });
};

main();
