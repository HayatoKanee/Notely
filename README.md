# Notely
Notely is a note-taking application that aims to help students take notes during their studies.

## Team members
The members of the team are:
- *Paul Cheung*
- *Ziwen Wang*
- *Wenxuan Wang*
- *Yuze Bai*
- *Ryan Tsoi*
- *Heli Ip*
- *Jeremy Lin*

## Deployed version of the application
The deployed version of the application can be found at *<https://notely-winnie.herokuapp.com/>*.

## Installation instructions
To install the software and use it in your local development environment, you must first set up and activate a local development environment.  From the root of the project:

```
$ virtualenv venv
```
```
$ source venv/bin/activate
```

Install all required packages:

```
$ pip3 install -r requirements.txt
```

Migrate the database:

```
$ python3 manage.py migrate
```

Seed the development database with:

```
$ python3 manage.py seed
```

Run all tests with:
```
$ python3 manage.py test
```

Collect all static files with:
```
$ python3 manage.py collectstatic
```

Redis is required for the ASGI set up. You can install redis by:
```
$ sudo apt install redis-server
```
Run server with(for development and testing ONLY):
```
$ daphne -e ssl:8000:privateKey=key.pem:certKey=cert.pem notely.asgi:application
```
Celery for background tasks:
```
$ celery -A notely worker -l INFO
```

*The above instructions should work in your version of the application.  If there are deviations, declare those here in bold.  Otherwise, remove this line.*

## Sources
The packages used by this application are specified in `requirements.txt`

### JavaScript Library
- [Fabric](http://fabricjs.com/)
- [CodeMirror](https://codemirror.net/)
- [Bootstrap](https://getbootstrap.com/)
- [jQuery](https://jquery.com/)
- [jQuery UI](https://jqueryui.com/)
- [FullCalendar](https://fullcalendar.io/)
- [jsPDF](https://parall.ax/products/jspdf)

### Images
signup_login.jpg:https://www.wikihow.com/Take-Better-Notes

select.png:https://www.flaticon.com/free-icon/click_2767163?term=select&page=1&position=12&origin=search&related_id=2767163

pen.png:https://www.flaticon.com/free-icon/pen_1860115

addFolder.png:https://www.flaticon.com/free-icon/new-folder_9517944?term=add&page=1&position=8&origin=search&related_id=9517944

folder.png:https://www.flaticon.com/free-icon/folder_1383970?term=folder&page=1&position=2&origin=search&related_id=1383970

notebook.png:https://www.flaticon.com/free-icon/notebook_2904859?term=notebook&page=1&position=2&origin=search&related_id=2904859

bell.png:https://www.flaticon.com/free-icons/notification-bell

erase.png:https://www.clipartmax.com/middle/m2i8Z5K9b1m2m2N4_eraser-icon-eraser-icon-png/

linkPage.png:https://www.flaticon.com/free-icon/link_455691?term=link&page=1&position=2&origin=search&related_id=455691

templates.png:https://www.flaticon.com/free-icon/layout_721764?term=templates&page=1&position=7&origin=search&related_id=721764

share.png:https://www.flaticon.com/free-icon/share_1828954?term=share&page=1&position=7&origin=search&related_id=1828954

event.png:https://www.flaticon.com/free-icon/event_2558957?term=event&page=1&position=7&origin=search&related_id=2558957
