
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

    def formatday(self, day):
        tdContent = ""
        for event in self.events.filter(start_time__day=day):
                tdContent += f'<li> {event.title} </li>'
        if (day == datetime.now().day):      
            return f"<td bgcolor='MediumSeaGreen'><span class='date'>{day}</span><ul> {tdContent} </ul></td>"
        if (day != 0):
            return f"<td><span class='date'>{day}</span><ul> {tdContent} </ul></td>"
        return '<td></td>'

    def formatweek(self, theWeek):
        week = ''
        for day,weekday in theWeek:
            week += self.formatday(day)
        return f'<tr> {week} </tr>'

    def formatmonth(self, withyear=True):
        cal = f'<table border="5" cellpadding="0" cellspacing="0" class="calendar">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week)}\n'
        cal +=f'</table>'
        return cal

