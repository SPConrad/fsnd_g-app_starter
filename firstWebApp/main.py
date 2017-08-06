# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import webapp2
import cgi

form = """
<form method="post">
    What is your birthday?
    
	<label>
        Month
        <input type="text" name="month" value="%(month)s">
    </label>
    <label>
        Day
        <input type="text" name="day" value="%(day)s">
    </label>
    <label>
        Year
        <input type="text" name="year" value="%(year)s">
    </label>
    <div style="color: red">%(error)s</div>
    <br>
    <br>
	<input type="submit">
</form>
"""

class MainPage(webapp2.RequestHandler):
    def write_form(self, error="", month="", day="", year=""):
        self.response.out.write(form % {
            "error": error, 
            "month": month, 
            "year": year, 
            "day": day 
            })

    def get(self):
        self.write_form()

    def post(self):
        user_month = self.request.get('month')
        user_day = self.request.get('day')
        user_year = self.request.get('year')

        month = valid_month(user_month)
        day = valid_day(user_day)
        year = valid_year(user_year)

        if not (day and month and year):
            self.write_form("Invalid date", easy_escape(user_month), easy_escape(user_day), easy_escape(user_year))
        else: 
            self.redirect("/thanks")


months = ['january',
          'february',
          'march',
          'april',
          'may',
          'june',
          'july',
          'august',
          'september',
          'october',
          'november',
          'december']
#this does not work
#def valid_month(month):
#    if (months.index(month.lower()) != ValueError):
#        return "January" #month.title()
#    else:
#        return "None"

#make a dictionary
#create a mapping of the first 3 letters of the month in lowercase and match that with the month

month_abbvs = dict((m[:3].lower(), m) for m in months)
#month_days = dict(for d in days, for m in months)

#func with dictionary
def valid_month(month):
    if month:
        short_month = month[:3].lower()
        return month_abbvs.get(short_month)

#dumb version but it works 
def valid_day(day):
    if day.isdigit():
        if int(day) <= 31 and int(day) > 0:
            return int(day)

def valid_year(year):
    if year.isdigit():
        if int(year) <= 2020 and int(year) > 1900:
            return int(year)

def easy_escape(s):
    return cgi.escape(s, quote = True)

def escape_html(s):
    for (i, o) in (("&", "&amp;"),
                    (">", "&gt;"),
                    ("<", "&lt;"),
                    ('"', "&quot")):
        s = s.replace(i, o)

    return s


class ThanksHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("Thanks! That is a valid date.")

app = webapp2.WSGIApplication([
        ('/', MainPage),
        ('/thanks', ThanksHandler)
], debug=True)
