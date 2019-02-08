exports.main = (req, res) => {
    let url = req.query.url || req.body.url;
  
    var cloudscraper = require('cloudscraper');
    cloudscraper.get(url, function(error, response, body) {
    if (error) {
      console.log('Error occurred');
    } else {
      console.log(body, response);
      res.status(200).send(body)
    }
  });
  };