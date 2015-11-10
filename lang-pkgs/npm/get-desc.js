var bluebird = require('bluebird');
var fetch = require('node-fetch');
fetch.Promise = bluebird;
var path = require('path');
var downloadUrl = "https://api.npmjs.org/downloads/point/last-month/";
var npmStat = require('npm-stats')(); //('http://127.0.0.1:5984/', {modules: 'npm'});
var fs = bluebird.promisifyAll(require('fs'));

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

var readOrCreateList = function() {
  var file = 'list.json';
  return fs.readFileAsync(file, 'utf-8')
  .then(function(content) {
    var list = JSON.parse(content);
    return list;
  })
  .catch(function() {
    var list;
    return getAllPkg()
    .then(function(content) {
      list = content;
      return fs.writeFileAsync(file, content, 'utf-8');
    })
    .then(function() {
      return list;
    });
  });
};

var readCursor = function() {
  var file = 'cursor.dat';
  return fs.readFileAsync(file, 'utf-8')
  .then(function(content) {
    return content;
  })
  .catch(function(err) {
    return -1;
  });
};

var updateCursor = function(cur) {
  var file = 'cursor.dat';
  return fs.writeFileAsync(file, cur.toString(), 'utf-8')
};

var process = function() {
  var out = bluebird.promisifyAll(fs.createWriteStream('results.json', {flags: 'a'}));

  readOrCreateList()
  .then(function(list) {
    return readCursor()
    .then(function(cursor) {
      return list.slice(cursor + 1);
    });
  })
  .each(function(pkgName, idx, len) {
    console.info(idx + " of " + len);
    return getDescForPkg(pkgName)
    .then(function(result) {
      return out.writeAsync(JSON.stringify(result) + '\n');
    })
    .then(function() {
      return updateCursor(idx);
    });
  })
  .then(function() {
    return out.endAsync();
  })
  .catch(function(err) {
    console.error(err);
  });
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
