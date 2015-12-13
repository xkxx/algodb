var bluebird = require('bluebird');
var fetch = require('node-fetch');
fetch.Promise = bluebird;
var path = require('path');
var downloadUrl = "https://api.npmjs.org/downloads/point/last-month/";
var npmStat = require('npm-stats')('http://127.0.0.1:5984/', {modules: 'npm'});
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
    getDownloadsForPkg(pkgName)
  ]).then(function(res) {
    var json = res[0];
    var downloads = res[1];

    var name = json.name;
    var desc = json.description;
    var keywords = json.keywords;

    var time = json.time;
    var ctime = time? json.time.created : json.ctime;
    var mtime = time? json.time.modified : json.mtime;

    var verLatest = json['dist-tags'].latest;

    // process readme
    var readme = json.readme;
    var readmeFile = json.readmeFilename;
    var readmeType = path.extname(readmeFile).slice(1);

    // find repo
    var repository = json.repository;
    var github;

    if (repository && repository.url) {
      github = repository.url.match(matchGithub);
    }
    else if (typeof json.homepage == 'string') {
      github = json.homepage.match(matchGithub);
    }

    if (github) {
      github = github.slice(1, 3);
    }

    return {
      name: name,
      desc: desc,
      timeUpdated: mtime,
      timeCreated: ctime,
      latest: verLatest,
      keywords: keywords,
      readme: readme,
      readmeFile: readmeFile,
      readmeType: readmeType,
      repo: repository? repository.url : null,
      github: github,
      downloads: downloads
    };
  });
};

exports.getDescForPkg = getDescForPkg;

var moduleListAsync = bluebird.promisify(npmStat.list);
var getAllPkgs = function() {
  return fetch('http://localhost:5984/npm/_all_docs')
  .then((res) => res.json())
  .then(function(res) {
    return res.rows.map((item)=>item.key);
  });
};

exports.getAllPkgs = getAllPkgs;

var readOrCreateList = function() {
  var file = 'list.json';
  return fs.readFileAsync(file, 'utf-8')
  .then(function(content) {
    var list = JSON.parse(content);
    return list;
  })
  .catch(function() {
    var list;
    return getAllPkgs()
    .then(function(content) {
      list = content;
      return fs.writeFileAsync(file, JSON.stringify(list), 'utf-8');
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
    return parseInt(content,10);
  })
  .catch(function(err) {
    return -1;
  });
};

var updateCursor = function(cur) {
  var file = 'cursor.dat';
  return fs.writeFileAsync(file, cur.toString(), 'utf-8');
};

var main = function() {
  var out = bluebird.promisifyAll(fs.createWriteStream('results.json', {flags: 'a'}));
  var list, cursor;

  readOrCreateList()
  .then(function(r) {
    list = r;
    return readCursor();
  })
  .then(function(r) {
    cursor = r + 1;
    return list.slice(cursor);
  })
  .each(function(pkgName, idx) {
    if (pkgName.startsWith("_design/")) {
        console.info("Skipping design doc " + pkgName);
        return;
    }
    console.info(pkgName + " " + (cursor + idx) + " of " + list.length);
    return getDescForPkg(pkgName)
    .then(function(result) {
      return out.writeAsync(JSON.stringify(result) + '\n');
    })
    .then(function() {
      return updateCursor(cursor + idx);
    })
    .catch(function(error) {
      console.error(error);
      throw error;
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
  if (process.argv.length == 1) {
    main();
  }
  else {
    var pkgName = process.argv.slice(-1)[0];
    if (pkgName) {
      getDescForPkg(pkgName)
      .then(function(result) {
        console.info(JSON.stringify(result));
      })
      .catch(function(err) {
        console.error(err);
      });
    }
  }
}
