var fetch = require('node-fetch');
var path = require('path');
var downloadUrl = "https://api.npmjs.org/downloads/point/last-month/";
var npmStat = require('npm-stats')(); //('http://127.0.0.1:5984/', {modules: 'npm'});
var bluebird = require('bluebird');

var matchGithub = /github.com\/([\w\d-_]*)\/([\w\d-_]*)/;

var getDownloadsForPkg = function(pkgName) {
  return fetch(downloadUrl + pkgName)
  .then(function(res) {
    return res.json();
  }).then(function(json) {
    return json.downloads;
  });
};

var getDescForPkg = function(pkgName) {
  var pkg = bluebird.promisifyAll(npmStat.module(pkgName));

  return bluebird.all([
    pkg.infoAsync(),
    pkg.starsAsync(),
    getDownloadsForPkg(pkgName)
  ]).then(function(res) {
    var json = res[0];
    var stars = res[1].length;
    var downloads = res[2];

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
      latest: verLatest,
      keywords: keywords,
      readme: readme,
      readmeFile: readmeFile,
      readmeType: readmeType,
      repo: repository? repository.url : null,
      github: github,
      stars: stars,
      downloads: downloads
    };
  });
};

exports.getDescForPkg = getDescForPkg;

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

exports.getAllPkgs = getAllPkgs;
