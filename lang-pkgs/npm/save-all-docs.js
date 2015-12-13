var bluebird = require('bluebird');
var redis = require("redis"),
    r = bluebird.promisifyAll(redis.createClient());

var npmLibs = require('./get-desc');
