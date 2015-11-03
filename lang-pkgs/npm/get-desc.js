var fetch = require('node-fetch');
var path = require('path');
var registry = "https://registry.npmjs.com/";
var downloadUrl = "https://api.npmjs.org/downloads/point/last-month/";
var npmStat = require('npm-stats')(registry);
var bluebird = require('bluebird');

var matchGithub = /github.com\/([\w\d-_]*)\/([\w\d-_]*)/;

var getDescForPkg = function(pkgName) {
  return fetch(registry + pkgName)
  .then(function(res) {
    return res.json();
  }).then(function(json) {
    var name = json.name;
    var desc = json.description;
    var keywords = json.keywords;

    var verLatest = json['dist-tags'].latest;

    // process readme
    var readme = json.readme;
    var readmeFile = json.readmeFilename;
    var readmeType = path.extname(readmeFile).slice(1);

    // find repo
    var repository = json.repository;
    var github;
    if (repository) {
      github = repository.url.match(matchGithub);
    }
    else {
      github = json.homepage.match(matchGithub);
    }
    if (github) {
      github = github.slice(1, 3);
    }

    return {
      name: name,
      desc: desc,
      keywords: keywords,
      readme: readme,
      readmeFile: readmeFile,
      readmeType: readmeType,
      repo: repository? repository.url : null,
      github: github
    };
  });
};

var getDescForPkg = getDescForPkg;

var getDownloadsForPkg = function(pkgName) {
  return fetch(downloadUrl + pkgName)
  .then(function(res) {
    return res.json();
  }).then(function(json) {
    return downloads;
  });
};

exports.getDownloadsForPkg = getDownloadsForPkg;

var getStatsForPkg = function(pkgName) {
  var pkg = bluebird.promisifyAll(npmStat.module(pkgName));

  return pkg.starsAsync(function(stars) {
    return stars.length;
  });
};

exports.getStatsForPkg = getStatsForPkg;

var moduleListAsync = bluebird.promisify(npmStat.list);
var getAllPkgs = function() {
  return moduleListAsync();
};

if(require.main === module) {
  var pkgName = process.argv.slice(-1)[0];
  if (pkgName) {
    getDescForPkg(pkgName)
    .then(function(result) {
      console.info(result);
    })
    .catch(function(err) {
      console.error(err);
    });
  }
}
