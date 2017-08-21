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
jinja_env.globals.update(vars={})

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), 
                                autoescape = True)

def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model):
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("blogpost.html", p = self)

class Users(db.Model):
    username = db.StringProperty(required = True)
    #"(name + pw + salt), salt"
    password = db.StringProperty(required = True)
    email = db.StringProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)



#registration

#login
#cookie

#log out
#kill cookie


class NewPost(Handler):
    def render_new_post(self, error=""):
        self.render("newpost.html", error=error)

    def get(self):
        self.render_new_post()

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        #add a check for title and body > X characters
        if title and body:
            bp = Blog(title = title, body = body)
            bp.put()
            #todo: redirect to the new post
            print(bp.key().id())
            self.redirect('/blog/?id=%s' % bp.key().id())
        else:
            #todo: conditional error message
            error = "Sorry, you're missing the title, body, or both. Please try again"
            self.render_new_post(error)

class ViewBlogPost(Handler):
    def render_blog_post(self, title="", body="", error=""):
        self.render("blogpost.html", title=title, body=body, error=error)
    
    def get(self):
        post = Blog.get_by_id(int(self.request.get("id")))
        self.render_blog_post(title=post.title, body=post.body)

class SignUp(Handler):
    def render_sign_up(self, username="", password="", verify="", email="", error=""):
        self.render("signup.html", username = username, password = password, verify=verify, email=email, error=error)

    def get(self):
        self.render_sign_up()

    def post(self):
        _username = self.request.get("username")
        _password = self.request.get("password")
        _verify = self.request.get("verify")
        _email = self.request.get("email")

        if not _password == _verify:
            _password = None

        if _username and _password and _email:
            hashedPW = make_pw_hash(_username, _password)
            #user = Users(username = _username, password = _password, email = _email)
            #user.put()
            #print(user.key().id())
            self.response.headers.add_header('Set-Cookie', 'userID=%s; Path=/' % str(hashedPW))
            self.redirect('/')
#class Login(Hanlder):
 #   def render_login(self, "username")

class MainPage(Handler):
    def render_front(self, title="", body="", error=""):        
        posts = db.GqlQuery("SELECT * from Blog ORDER BY created DESC")
        for post in posts:
            print post.key().id()
        self.render("home.html", title=title, body=body, error=error, posts=posts)
    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get("title")
        art = self.request.get("art")

        if title and art:
            a = Art(title = title, art = art)
            a.put()

            self.redirect('/')
        else:
            error = "Error: Please enter both a title and a body for the post"
            self.render_front(title, art, error)



def make_secure_val(s):
    return "%s|%s" % (s, hash_str(s))

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
    print salt
    hashed = hashlib.sha256(name + pw + salt).hexdigest()
    return "%s|%s" % (hashed, salt)





app = webapp2.WSGIApplication([('/', MainPage),
                              ('/blog/([0-9]+)', ViewBlogPost),
                              ('/newpost', NewPost),
                              ('/signup', SignUp)], debug=True)