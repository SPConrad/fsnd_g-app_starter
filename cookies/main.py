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
import hashlib
import hmac
import random
import string
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

salt = ""

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainPage(Handler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        visits = 0
        visit_cookie_str = self.request.cookies.get('visits')
        if visit_cookie_str:
            cookie_val = check_secure_val(visit_cookie_str)
            if cookie_val:
                visits = (int(cookie_val))

        #make sure visits is an int
        # if visits.isdigit():
        #     visits = int(visits) + 1
        # else: 
        #     visits = 0
        visits += 1

        #new_cookie = "%s|%s" % (user_id, hash(username + pw))

        #get the cookie with the ID of user_id
        user_cookie_str = self.request.cookies.get('user_id')
        #if it exists
        if user_cookie_str:
            #check that it is valid
            user_cookie = check_secure_val(user_cookie_str)
            #if it is, redirect to welcome page
            if user_cookie:
                user = user_cookie

        
        # have to convert visits to a string before sending
        new_cookie_val = make_secure_val(str(visits))

        self.response.headers.add_header('Set-Cookie', 'user_id=%s' % new_cookie_val)

        if visits > 10000:
            self.write("You are amazing!")
        else:
            self.write("You've been here %s times" % visits)

def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))

def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    print(salt)
    hashed = hashlib.sha256(name + pw + salt).hexdigest()
    return "%s,%s" % (hashed, salt)

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

#def hash_str(s):
#    return hmac.new(secret, s).hexdigest()


app = webapp2.WSGIApplication([('/', MainPage)], debug=True)