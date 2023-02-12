gapi.load('client:auth2', function() {
    console.log("test1")
  gapi.client.init({
    apiKey: 'AIzaSyDOfaJ3As7QXgrdKUrOv541oFDZutYE0q8',
    clientId: '588566071525-5p0gps8skl9gr5j9919r8gob501jqa01.apps.googleusercontent.com',
    scope: 'https://www.googleapis.com/auth/calendar'
  }).then(function() {
    console.log("test2")
    if (gapi.auth2.getAuthInstance().isSignedIn.get()) {
        console.log("User is signed in");
      } else {
        console.log("User is not signed in");
      }
    gapi.auth2.getAuthInstance().signIn();
    if (gapi.auth2.getAuthInstance().isSignedIn.get()) {
        console.log("User is signed in");
      } else {
        console.log("User is not signed in");
      }
    gapi.client.load('calendar', 'v3', function() {
        gapi.client.calendar.events.list({
          calendarId: 'primary',
          timeMin: (new Date()).toISOString(),
          maxResults: 100,
          singleEvents: true,
          orderBy: 'startTime'
        }).then(function(response) {
          var events = response.result.items;
          $('#calendar').fullCalendar({
            events: events,
            eventClick: function(calEvent, jsEvent, view) {
              alert('Event: ' + calEvent.title);
              alert('Coordinates: ' + jsEvent.pageX + ',' + jsEvent.pageY);
              alert('View: ' + view.name);
            }
          });
        });
      });
  });
});

$(document).ready(function() {
    $('#login-google').on('click', function() {
      gapi.auth2.getAuthInstance().signIn();
    });
  });

  gapi.client.calendar.events.insert({
    calendarId: 'primary',
    resource: {
      summary: 'Test Event',
      start: {
        dateTime: '2023-02-11T10:00:00',
        timeZone: 'America/Los_Angeles'
      },
      end: {
        dateTime: '2023-02-11T11:00:00',
        timeZone: 'America/Los_Angeles'
      }
    }
  }).then(function(response) {
    if (gapi.auth2.getAuthInstance().isSignedIn.get()) {
      console.log(response.result);
    } else {
      console.log('User is not signed in.');
    }
  });