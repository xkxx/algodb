/**
 * The interface to the database. Used for searching and storing.
 */

var async = require('async');
var request = require('request');
var map = require('objmap');
var isarray = require('isarray');
var marked = require('marked');
marked.setOptions({
  renderer: new marked.Renderer(),
  gfm: true,
  tables: true,
  breaks: false,
  pedantic: false,
  sanitize: true,
  smartLists: true,
  smartypants: false
});
var unique = require('array-unique');

var MAX_RESULTS_PER_PAGE = 50;

var ELASTIC_SEARCH_URL = 'http://localhost:9200/throwtable/';
var ELASTIC_SCROLL_URL = 'http://localhost:9200/';

/**
 * Quick way to get json from a url.
 * @param  {String}   url The URL to request JSON from.
 * @param  {Callback} cb  The callback
 * @return {Object[]} err, body
 */
function getJSON(url, cb) {
  request(url, function(err, res, body) {
    cb(err, JSON.parse(body));
  });
}

module.exports = {
  /**
   * Searches the elastic search db.
   * @param  {String} query The raw text query
   * @param  {Callback} cb The response callback
   * @return {Object} res A search result object with the following data
   * @return {Object} res.error The error
   * @return {Object} res.hits The hits from elasticsearch
   */
  search: function(query, cb) {
    var self = this;
    var url = ELASTIC_SEARCH_URL + 'algorithm/_search';
    var body = {
      query: {
        multi_match: {
          query: query,
          fields: ['name^3', 'tag_line^1.5', 'description'],
          fuzziness: 'AUTO'
        }
      },
      min_score: 1,
      size: MAX_RESULTS_PER_PAGE,
    };
    request({
      url: url,
      body: body,
      json: true
    }, function(error, response, body) {
      var res = {};
      res.error = error;

      // Add the algorithm response data if there wasn't an error
      if (!error && response.statusCode === 200) {
        res.hits = body.hits.hits;

        // Get a list of algorithm ids
        var ids = res.hits.map(function(alg) {
          return alg._id;
        });

        res.limitImpls = true;

        self.get_search_results_from_algorithm_ids(ids, res, function(err, results) {
          cb(error, res);
        });
      } else {
        cb(error, res);
      }
    });
  },

  /**
   * Returns organized search results
   * @param {String[]} ids A list of algorithm ids
   * @param {Object} res (res = {}, res.hits = body.hits.hits;)
   * @param {Callback} cb The callback
   */
  get_search_results_from_algorithm_ids: function(ids, res, cb) {
    // Prepare the implemenatation queries
    var self = this;
    var algorithmImplementationQueries = ids.map(function(id) {
      return function(queryCb) {
        var options = {
          id: id,
          // limitImpls: res.limitImpls
        };
        if (res.language) {
          options.language = res.language;
        }
        self.get_implementations(options, function(err, impls) {
          queryCb(err, {
            id: id,
            hits: impls
          });
        });
      };
    });
    // Execute the queries in parallel
    async.parallel(algorithmImplementationQueries, function(queryErr, implQueryData) {
      for (var i = 0; i < res.hits.length; ++i) {
        var algorithm = res.hits[i];

        algorithm.url = '/' + algorithm._id;

        var impls = implQueryData.filter(function(impls) {
          return impls.id === algorithm._id;
        })[0];
        algorithm.implementations = impls.hits.sort(function (a, b) {
          var aLang = a._source.language.toLowerCase();
          var bLang = b._source.language.toLowerCase();
          return (aLang > bLang) ? 1 : ((bLang > aLang) ? -1 : 0);
        });

        // Convert npm markdown to html
        for (var j = 0; j < algorithm.implementations.length; ++j) {
          if (algorithm.implementations[j]._source.source === 'npm') {
            var instruction = algorithm.implementations[j]._source.instruction;
            instruction.html = marked(instruction.content);
          }
        }

        // Add list of languages
        algorithm.implementationLanguages = unique(algorithm.implementations.map(function(impl) {
          return impl._source.language;
        }).sort(function(a, b) {
          a = a.toLowerCase();
          b = b.toLowerCase();
          return (a > b) ? 1 : ((b > a) ? -1 : 0);
        }));

        if (res.limitImpls) {
          algorithm.implementations = algorithm.implementations.splice(0, 5);
        }

        // Remove implementations that aren't in the queried language
        if (res.language) {
          algorithm.implementations = algorithm.implementations.filter(function(impl) {
            return impl._source.language.toLowerCase() === res.language.toLowerCase();
          });
        }
      }

      cb(null, res);
    });
  },

  /**
   * Gets results by programming language.
   * @param {String} language A language
   * @param {Callback} cb The callback
   */
  search_by_language: function(language, cb) {
    var self = this;
    var url = ELASTIC_SEARCH_URL + 'implementation/_search';
    var body = {
      query: {
        match: {
          language: language
        }
      },
      size: MAX_RESULTS_PER_PAGE
    };
    request({
      url: url,
      body: body,
      json: true
    }, function(error, response, body) {
      if (!error && response.statusCode === 200) {
        var hits = body.hits.hits;
        var algorithmIds = hits.map(function(hit) {
          return hit._source.algorithm[0];
        });

        // Fix Kexiang's bug with npm double arrays
        algorithmIds = algorithmIds.map(function(id) {
          if (isarray(id)) {
            return id[0];
          } else {
            return id;
          }
        }).filter(function(id) {
          // Some of the values are [[null, null]] (!!!)
          return !!id;
        });

        self.get_algorithms_by_ids(algorithmIds, function(err, algorithms) {
          var res = {
            hits: algorithms,
            language: language
          };
          self.get_search_results_from_algorithm_ids(algorithmIds, res, function(err, results) {
            cb(err, results);
          });
        });
      } else {
        cb(error);
      }
    });
  },

  /**
   * Search by algorithm ID
   * @param {String} algorithmId The id of the algorithm
   * @param {Callback} cb The callback
   */
  search_by_algorithm_id: function(algorithmId, cb) {
    var self = this;
    self.get_algorithms_by_ids([algorithmId], function(err, algorithms) {
      var res = {};
      res.hits = algorithms;
      self.get_search_results_from_algorithm_ids([algorithmId], res, function(err, results) {
        cb(err, results);
      });
    });
  },

  /**
   * Gets algorithm hits for all ids
   * @param {String[]} algorithmIds A list of algorithm ids
   * @param {Callback} cb The callback
   */
  get_algorithms_by_ids: function(algorithmIds, cb) {
    var url = ELASTIC_SEARCH_URL + 'algorithm/_search';
    var body = {
      query: {
        terms: {
          _id: algorithmIds
        }
      },
      size: MAX_RESULTS_PER_PAGE
    };
    request({
      url: url,
      body: body,
      json: true
    }, function(error, response, body) {
      var hits;
      if (!error && response.statusCode === 200) {
        hits = body.hits.hits;
      }
      cb(error, hits);
    });
  },

  /**
   * Gets all algorithm names in the database
   * @param  {Callback} cb The callback
   * @return {String[]} A list of algorithm names
   */
  get_algorithms: function(cb) {
    var url = ELASTIC_SEARCH_URL + 'algorithm/_search';
    var body = {
      fields: ['name'],
      size: 10000,
      query: {
        match_all: {}
      }
    };
    request({
      url: url,
      body: body,
      json: true
    }, function(error, response, body) {
      var names;
      if (!error && response.statusCode === 200) {
        var hits = body.hits.hits;
        names = hits.map(function(hit) {
          return {
            name: hit.fields.name[0],
            id: hit._id
          };
        });
      }
      cb(error, names);
    });
  },

  /**
   * Gets a count of the number of implementations in each language.
   * @param  {Function} cb The response callback
   * @return {Object}      A map from language to implementation in that language count
   */
  get_languages: function(cb) {
    var url = ELASTIC_SEARCH_URL + 'implementation/_search?search_type=scan&scroll=1m';
    var body = {
      fields: ['language'],
      // from: 1000,
      size: 100000,
      query: {
        match_all: {}
      },
    };
    request({
      url: url,
      body: body,
      json: true
    }, function(error, response, body) {
      var scrollId = body._scroll_id;
      if (!error && response.statusCode === 200) {
        url = ELASTIC_SCROLL_URL + '_search/scroll?scroll=5m&scroll_id=' + scrollId;
        body = {};
        request({
          url: url,
          body: body,
          json: true
        }, function(error, response, body) {
          var languages = {};

          if (!error && response.statusCode === 200) {
            var hits = body.hits.hits;
            for (var i = 0; i < hits.length; ++i) {
              var lang = hits[i].fields.language[0];
              if (!languages[lang]) {
                languages[lang] = 0;
              }
              ++languages[lang];
            }
          }

          cb(error, languages);
        });
      }
    });
  },

  /**
   * Gets all the implementation documents for a given algorithm id
   * @param {String} algorithmId The algorithm id
   * @param {Function} cb The response callback
   * @return {Object} res A list of implementations
   * @return {Object} res.error The error
   * @return {Object} res.hits The hits
   */
  get_implementations: function(options, cb) {
    var url = ELASTIC_SEARCH_URL + 'implementation/_search';
    var algorithmId = options.id;
    var language = options.language;
    var body = {
      query: {
        bool: {
          must: [{
            match: {
              algorithm: algorithmId
            }
          }]
        }
      },
      size: (options.limitImpls ? 5 : 1000)
    };
    request({
      url: url,
      body: body,
      json: true,
    }, function(error, response, body) {
      var hits;
      if (!error && response.statusCode === 200) {
        hits = body.hits.hits;
      }

      cb(error, hits);
    });
  },

  /**
   * Gets a random algorithm id
   * @param {Callback} cb The callback
   */
  get_random_algorithm: function(cb) {
    var url = ELASTIC_SEARCH_URL + 'algorithm/_search';
    var body = {
      size: 1,
      query: {
        function_score: {
          query: {
            match_all: {}
          },
          random_score: {}
        }
      }
    };
    request({
      url: url,
      body: body,
      json: true
    }, function(error, response, body) {
      var hits;
      if (!error && response.statusCode === 200) {
        hits = body.hits.hits;
      }
      cb(error, hits[0]._id);
    });
  },

  get_categories: function(cb) {
    var url = ELASTIC_SEARCH_URL + 'category/_search';
    var body = {
      size: 1000,
      query: {
        match_all: {}
      }
    };
    request({
      url: url,
      body: body,
      json: true
    }, function(error, response, body) {
      var hits;
      if (!error && response.statusCode === 200) {
        hits = body.hits.hits;
      }
      cb(error, hits);
    });
  },

  /**
   * Gets the counts of the "algorithm", "category", and "implementation" mappings.
   * Assumes never fails.
   * @param  {Callback} cb The response callback
   * @return {Object}   res["algorithm", "category", "implementation"] The number of documents in this index
   */
  count_summary: function(cb) {
    var urlBase = ELASTIC_SEARCH_URL;
    // TODO(grant) make prettier using ["algorithm", "category", "implementation"]
    async.parallel({
      algorithm: function(c) { getJSON(urlBase + 'algorithm/_count', c); },
      category: function(c) { getJSON(urlBase + 'category/_count', c); },
      implementation: function(c) { getJSON(urlBase + 'implementation/_count', c); },
    }, function(err, data) {
      var mappedData = map(data, function(countObj) {
        return countObj.count;
      });
      cb(err, mappedData);
    });
  }
};
