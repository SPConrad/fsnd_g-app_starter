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

import os
import jinja2
import webapp2
import cgi
import re

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))
jinja_env.globals.update(vars={})

nameReg = re.compile("^[a-zA-Z0-9_-]{3,20}$")
passwordReg = re.compile("^.{3,20}$")
emailReg = re.compile("^[\S]+@[\S]+.[\S]+$|^$")

errorLabel = """<label style="color: red">%(error)s</label>"""

invalidText = "That's not a valid %(type)s"

mismatchText = "Passwords do not match"


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
        
    #feel free to steal these for basic template rendering
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class MainPage(Handler): 
    def get(self):
        self.render("signup.html")

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        user_email = self.request.get('email')
        nameError = ""
        passwordError = ""
        emailError = ""

        name = validate(nameReg, username)
        passwordMatch = match(password, verify)
        if passwordMatch:
            password_valid = validate(passwordReg, password)
        else:
            password_valid = False
        email = validate(emailReg, user_email)

        if not (name and passwordMatch and password and email):
            if not name:
                nameError = (errorLabel % {"error": (invalidText % {"type" : "username"})})
            if not passwordMatch:
                passwordError = (errorLabel % {"error": mismatchText})
            elif not password:
                passwordError = (errorLabel % {"error": (invalidText % {"type" : "password"})})
            if not email: 
                emailError = (errorLabel % {"error": (invalidText % {"type" : "email"})})
            self.render("signup.html", vars = {
                "username": username, 
                "nameError": nameError, 
                "passwordError": passwordError, 
                "email": user_email, 
                "emailError": emailError
                })
        else:
            #set the cookie
            #hash = hashed(username + pw)
            #cookie = user_id_number|hash

            #hash_val = make_secure_val("%s + %s" % (name, password))
            #self.response.headers.add_header('Set-Cookie', 'user_id=%s' % user_id_cookie)
            #self.redirect("/welcome")

class WelcomeHandler(Handler):
    def get(self):
        #look for the cookie
        user_name = self.request.get('username')
        self.render("success.html", username = user_name)

def check_secure_val(h):
    val = h.split('|')[0]
    if h == make_secure_val(val):
        return val


def make_secure_val(s):
    return "%s|%s" % (s, hash_str(s))

#md5 is not secure, but worked fine for testing purposes
def hash_str(s):
    return hashlib.md5(s).hexdigest()

secret = "secretValForHashing"

def match(str1, str2):
    if str1 == str2:
        return True

def validate(expression, strToVal):
        return expression.match(strToVal)

app = webapp2.WSGIApplication([('/', MainPage),
                                ('/welcome', WelcomeHandler)],
                                debug=True)