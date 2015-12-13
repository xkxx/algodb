var bluebird = require('bluebird');
var redis = require("redis"),
    r = bluebird.promisifyAll(redis.createClient());

var npmLibs = require('./get-desc');

var main = function() {
  npmLibs.getAllPkgs()
  .each(function(pkg) {
    return r.saddAsync('pkgs', pkg);
  })
  .then(function() {
    console.info('all done');
  });
};
