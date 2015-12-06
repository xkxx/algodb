/**
 * The interface to the database. Used for searching and storing.
 */

var async = require('async');
var request = require('request');
var map = require('objmap');

var ELASTIC_SEARCH_URL = 'http://localhost:9200/throwtable/';

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
      }
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

        // Prepare the implemenatation queries
        var algorithmImplementationQueries = ids.map(function(id) {
          return function(queryCb) {
            self.get_implementations(id, function(err, impls) {
              queryCb(err, {
                id: id,
                hits: impls.hits
              });
            });
          };
        });
        // Execute the queries in parallel
        async.parallel(algorithmImplementationQueries, function(queryErr, implQueryData) {
          for (var i = 0; i < res.hits.length; ++i) {
            var algorithm = res.hits[i];

            var impls = implQueryData.filter(function(impls) {
              return impls.id === algorithm._id;
            })[0];
            algorithm.implementations = impls.hits;
          }
          cb(error, res);
        });
      } else {
        cb(error, res);
      }
    });
  },

  /**
   * Gets all the implementation documents for a given algorithm id
   * @param {String} algorithmIds The algorithm id
   * @param {Function} cb The response callback
   * @return {Object} res A list of implementations
   * @return {Object} res.error The error
   * @return {Object} res.hits The hits
   */
  get_implementations: function(algorithmId, cb) {
    var url = ELASTIC_SEARCH_URL + 'implementation/_search';
    var body = {
      query: {
        match: {
          algorithm: algorithmId
        }
      }
    };
    request({
      url: url,
      body: body,
      json: true,
    }, function(error, response, body) {
      var res = {};
      res.error = error;

      if (!error && response.statusCode === 200) {
        res.hits = body.hits.hits;
      }

      cb(error, res);
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
