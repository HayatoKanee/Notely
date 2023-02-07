
from datetime import datetime, timedelta
from calendar import HTMLCalendar
from .models import Event
from datetime import date

#  reference: https://www.huiwenteo.com/normal/2018/07/24/django-calendar.html by Hui Wen ---Ryan
class EventCalendar(HTMLCalendar):
    def __init__(self,year,month,events):
        self.year = year
        self.month = month
        self.events = events
        super(EventCalendar, self).__init__()

    def formatday(self, day, events):
        events_today = events.filter(start_time__day=day)
        if (events_today != None):
            return daytd(day,events_today)
        return '<td></td>'

    def formatweek(self, theWeek, events):
        week = ''
        for day in theWeek:
            week += self.formatday(day, events)
        return f'<tr> {week} </tr>'

    def formatmonth(self, withyear=True):
        events = Event.objects.filter(start_time__year=self.year, start_time__month=self.month)

        calendar = f'<table border="5" cellpadding="0" cellspacing="0" class="calendar">\n'
        calendar += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        calendar += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            calendar += f'{self.formatweek(week, self.events)}\n'
        calendar +=f'</table>'
        return calendar

    def daytd(self, day , events):
        tdContent = ""
        for event in events:
                tdContent += f'<li> {event.title} </li>'
        if (day == datetime.now().day):      
            return f"<td bgcolor='MediumSeaGreen'><span class='date'>{day}</span><ul> {tdContent} </ul></td>"
        return f"<td><span class='date'>{day}</span><ul> {tdContent} </ul></td>"