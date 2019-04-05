var thingsboardServer = '192.168.1.202:8080';
var express = require('express'); // Express web server framework
var request = require('request'); // "Request" library
var cors = require('cors');
var querystring = require('querystring');
var cookieParser = require('cookie-parser');

var client_id = '1a1d0bc6659241cca24f2bc42b6d5971'; // Your client id
var client_secret = '50e07d60e093434ebbd8fd4fa57079f5'; // Your secret
var redirect_uri = 'http://192.168.1.202:8888/callback'; // Your redirect uri

var access_token;
var refresh_token;

//HTTP Response constants
const OK = 200;
const UNAUTHORIZED = 401;
const NOT_FOUND = 404;
const FORBIDDEN = 403;
const NO_CONTENT = 204;

/**
* Generates a random string containing numbers and letters
* @param  {number} length The length of the string
* @return {string} The generated string
*/
var generateRandomString = function(length) {
var text = '';
var possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';

for (var i = 0; i < length; i++) {
  text += possible.charAt(Math.floor(Math.random() * possible.length));
}
return text;
};

var stateKey = 'spotify_auth_state';

var app = express();

app.use(express.static(__dirname + '/public'))
 .use(cors())
 .use(cookieParser())
 .use(express.json());

app.get('/login', function(req, res) {

  var state = generateRandomString(16);
  res.cookie(stateKey, state);

  // your application requests authorization
  var scope = 'user-modify-playback-state user-read-private user-read-email';
  res.redirect('https://accounts.spotify.com/authorize?' +
    querystring.stringify({
      response_type: 'code',
      client_id: client_id,
      scope: scope,
      redirect_uri: redirect_uri,
      state: state,
    show_dialog: true
  }));
});

app.get('/callback', function(req, res) {

  // your application requests refresh and access tokens
  // after checking the state parameter

  var code = req.query.code || null;
  var state = req.query.state || null;
  var storedState = req.cookies ? req.cookies[stateKey] : null;

  if (state === null || state !== storedState) {
    res.redirect('/#' +
      querystring.stringify({
        error: 'state_mismatch'
      }));
  } else {
    res.clearCookie(stateKey);
    var authOptions = {
      url: 'https://accounts.spotify.com/api/token',
      form: {
        code: code,
        redirect_uri: redirect_uri,
        grant_type: 'authorization_code'
      },
      headers: {
        'Authorization': 'Basic ' + (new Buffer(client_id + ':' + client_secret).toString('base64'))
      },
      json: true
    };

    request.post(authOptions, function(error, response, body) {
      if (!error && response.statusCode === 200) {

        access_token = body.access_token;
        refresh_token = body.refresh_token;

        res.redirect("/#" +
          querystring.stringify({
            success: 'successful_login'
          }));

      } else {
        res.redirect('/#' + 
          querystring.stringify({
            error: 'invalid_token'
          }));
      }
    });
  }
});

app.get('/next_song', function(req, res) {
  if (access_token == null || refresh_token == null) {
    console.log('ERROR: No access token or refresh token.');
    res.status(UNAUTHORIZED);
    res.send({
        'error': 'No access token or refresh token.'
      });
  } else {

    var options = {
      url: 'https://api.spotify.com/v1/me/player/next',
      headers: { 'Authorization': 'Bearer ' + access_token },
      json: true
    };

    // use the access token to access the Spotify Web API
    request.post(options, function(error, response, body) {
      // Successfully played next song
      if (!error && response.statusCode === NO_CONTENT) {
        console.log('SUCCESS: Next Song Played');
        res.status(OK);
        res.send({
          'success': 'Next Song Played.'
        });
        // Invalid Access Token
      } else if (response.statusCode === UNAUTHORIZED) {
          refreshToken();
          var options = {
            url: 'https://api.spotify.com/v1/me/player/next',
            headers: { 'Authorization': 'Bearer ' + access_token },
            json: true
          };
          console.log('STATUS: Attempting to next song using new Access Token');
          request.post(options, function(error, response, body) {
            if (!error && response.statusCode === NO_CONTENT) {
              console.log('SUCCESS: Next Song Played');
              res.status(OK);
              res.send({
                'success': 'Next Song Played.'
              });

            } else {
              console.log('ERROR: Failed to refresh Access Token');
              res.status(UNAUTHORIZED);
              res.send({
                'error': 'Unable to refresh access token.'
              });
            }
          });
      } else if (response.statusCode === NOT_FOUND) {
        console.log('ERROR: No Active Spotify Instance');
        res.status(NOT_FOUND);
        res.send({
          'error': 'No active spotify instance.'
        });
      } else if (response.statusCode === FORBIDDEN) {
        console.log('ERROR: Spotify Premium Required');
        res.status(NOT_FOUND);
        res.send({
          'error': 'Spotify Premium Required'
        });
      } else {
        res.status(UNAUTHORIZED);
        res.send({
          'error': 'Error occured when posting next request'
        });
      }
    });
  }
});

function refreshToken() {
  // requesting access token from refresh token
  console.log("ERROR: Invalid Access Token, Getting new Token using Refresh Token");

  var authOptions = {
    url: 'https://accounts.spotify.com/api/token',
    headers: { 'Authorization': 'Basic ' + (new Buffer(client_id + ':' + client_secret).toString('base64')) },
    form: {
      grant_type: 'refresh_token',
      refresh_token: refresh_token
    },
    json: true
  };

  request.post(authOptions, function(error, response, body) {
    if (!error && response.statusCode === OK) {
      access_token = body.access_token;
      return true;
    } else {
      return false;
    }
  });
}

console.log('Listening on 8888');
app.listen(8888);
