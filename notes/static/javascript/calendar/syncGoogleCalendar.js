

function decodeJwtResponse(token) {
    let base64Url = token.split('.')[1]
    let base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    let jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
    return JSON.parse(jsonPayload)
}

let responsePayload;

// https://developers.google.com/identity/gsi/web/guides/handle-credential-responses-js-functions
window.handleCredentialResponse = (response) => {
    // decodeJwtResponse() is a custom function defined by you
    // to decode the credential response.
    responsePayload = decodeJwtResponse(response.credential);
    
    console.log("ID: " + responsePayload.sub);
    console.log('Full Name: ' + responsePayload.name);
    console.log('Given Name: ' + responsePayload.given_name);
    console.log('Family Name: ' + responsePayload.family_name);
    console.log("Image URL: " + responsePayload.picture);
    console.log("Email: " + responsePayload.email);
    console.log("Calendar ID: " + responsePayload.calendarId);

    }

    // https://developers.google.com/calendar/api/quickstart/js
    const CLIENT_ID = '588566071525-5p0gps8skl9gr5j9919r8gob501jqa01.apps.googleusercontent.com';
    const API_KEY = 'AIzaSyDOfaJ3As7QXgrdKUrOv541oFDZutYE0q8';

    const DISCOVERY_DOC = 'https://www.googleapis.com/discovery/v1/apis/calendar/v3/rest';
    const SCOPES = 'https://www.googleapis.com/auth/calendar';

    function handleClientLoad() {
        gapi.client.setApiKey(API_KEY);
        window.setTimeout(checkAuth, 1);
     }



function makeApiCall(){
    gapi.client.load('calendar', 'v3', function () { // load the calendar api (version 3)
                var request = gapi.client.calendar.events.insert
                ({
                    'calendarId': '24tn4fht2tr6m86efdiqqlsedk@group.calendar.google.com', 
    // calendar ID which id of Google Calendar where you are creating events. this can be copied from your Google Calendar user view.

                    "resource": resource 	// above resource will be passed here
                });                
})}

    let tokenClient;
    let gapiInited = false;
    let gisInited = false;

    document.getElementById('authorize_button').style.visibility = 'hidden';
    document.getElementById('signout_button').style.visibility = 'hidden';
// Callback after api.js is loaded.

    function gapiLoaded() {
      gapi.load('client', initializeGapiClient);
    }

//Callback after the API client is loaded. Loads the discovery doc to initialize the API.

    async function initializeGapiClient() {
      await gapi.client.init({
        apiKey: API_KEY,
        discoveryDocs: [DISCOVERY_DOC],
      });
      gapiInited = true;
      maybeEnableButtons();
    }

//Callback after Google Identity Services are loaded.

    function gisLoaded() {
      tokenClient = google.accounts.oauth2.initTokenClient({
        client_id: CLIENT_ID,
        scope: SCOPES,
        callback: '', // defined later
      });
      gisInited = true;
      maybeEnableButtons();
    }

//Enables user interaction after all libraries are loaded.

    function maybeEnableButtons() {
      if (gapiInited && gisInited) {
        document.getElementById('authorize_button').style.visibility = 'visible';
      }
    }

// Sign in the user upon button click.

    function handleAuthClick() {
      tokenClient.callback = async (resp) => {
        if (resp.error !== undefined) {
          throw (resp);
        }
        document.getElementById('signout_button').style.visibility = 'visible';
        document.getElementById('authorize_button').innerText = 'Refresh';
        await listUpcomingEvents();
      };

    console.log("test1")
      if (gapi.client.getToken() === null) {
        // Prompt the user to select a Google Account and ask for consent to share their data
        // when establishing a new session.
        tokenClient.requestAccessToken({prompt: 'consent'});
        console.log("test2", tokenClient)
      } else {
        // Skip display of account chooser and consent dialog for an existing session.
        tokenClient.requestAccessToken({prompt: ''});
        console.log("test3")
      }
    }


     //Sign out the user upon button click.

    function handleSignoutClick() {
      const token = gapi.client.getToken();
      if (token !== null) {
        google.accounts.oauth2.revoke(token.access_token);
        gapi.client.setToken('');
        document.getElementById('content').innerText = '';
        document.getElementById('authorize_button').innerText = 'Authorize';
        document.getElementById('signout_button').style.visibility = 'hidden';
      }
    }



    

