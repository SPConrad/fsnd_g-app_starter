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


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))
jinja_env.globals.update(vars={})

from google.appengine.ext import db

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
                visits = int(cookie_val)

        visits += 1

        new_cookie_val = make_secure_val(str(visits))

        self.response.headers.add_header('Set-Cookie', 'visits=%s' % new_cookie_val)
        self.write("You've been here %s times!" %visits)

#def hash_str(s):
#    return hashlib.md5(s).hexdigest()

def make_secure_val(s):
    return "%s|%s" % (s, hash_str(s))

# -----------------
# User Instructions
# 
# Implement the function check_secure_val, which takes a string of the format 
# s,HASH
# and returns s if hash_str(s) == HASH, otherwise None 

# def check_secure_val(h):
#     inputToCheck = h.split(",")
#     print inputToCheck[0]
#     print inputToCheck[1]
#     hashedInput = hash_str(inputToCheck[0])
#     print hashedInput
#     if hashedInput == inputToCheck[1]:
#         return inputToCheck[0]

#or

def check_secure_val(h):
    val = h.split('|')[0]
    if h == make_secure_val(val):
        return val

def hash_str(h):
    return hmac.new("secret", h).hexdigest()

#from udacity video
def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))

def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    hashed = hashlib.sha256(name + pw + salt).hexdigest()
    return "%s,%s" % (hashed, salt)


app = webapp2.WSGIApplication([('/', MainPage)], debug=True)



# #salt checker
# import random
# import string
# import hashlib

# def make_salt():
#     return ''.join(random.choice(string.letters) for x in xrange(5))

# # Implement the function valid_pw() that returns True if a user's password 
# # matches its hash. You will need to modify make_pw_hash.

# def make_pw_hash(name, pw, salt):
#     if not salt:
#         salt = make_salt()
#     h = hashlib.sha256(name + pw + salt).hexdigest()
#     return '%s,%s' % (h, salt)

# def valid_pw(name, pw, h):
#     salt = h.split(",")[1]
#     hashed_val = make_pw_hash(name, pw, salt)
#     if hashed_val == h:
#         return True
#     else:
#         return False

#h = make_pw_hash('spez', 'hunter2')
#print valid_pw('spez', 'hunter2', h)

