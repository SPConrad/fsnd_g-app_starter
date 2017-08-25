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
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), 
                                autoescape = True)
secret = "scruffy believes in this company"

nameReg = re.compile("^[a-zA-Z0-9_-]{3,20}$")
passwordReg = re.compile("^.{3,20}$")
emailReg = re.compile("^[\S]+@[\S]+.[\S]+$|^$")

errorLabel = """<label style="color: red">%(error)s</label>"""

invalidText = "That's not a valid %(type)s"

mismatchText = "Passwords do not match"

def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        #hash the cookie val. This is just the cookie
        cookie_val = make_secure_val(val)
        #Path=/ means it is valid for every page on the domain
        self.response.headers.add(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val)
        )

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)


    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(uid)

def render_post(response, post):
    response.out.write('<b>' + post.subject + '</b><br>')
    response.out.write(post.content)

class Blog(db.Model):
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("blogpost.html", p = self)

class Users(db.Model):
    name = db.StringProperty(required = True)
    #"(name + pw + salt), salt"
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()

    #this is a 'decorator', says you can call this method, on this object
    #normally the first parameter on a method on a class is "self", references that instance.
    #in this case we call it "cls" or "class", which means to the class user, not 
    #a specific instance of a user. 
    @classmethod
    def by_id(cls, uid):
        return User.get_by_id

    @classmethod
    def by_name(cls, name):
        #aka "SELECT * from USER where NAME = %s"
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name, pw, email = None):
        pw_hash = make_pw_hash(name, pw)
        return User(parent = users_key(),
                    name = name,
                    pw_hash = pw_hash,
                    email = email)

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



# class SignUp(Handler):
#     def render_sign_up(self, username="", password="", verify="", email="", error=""):
#         self.render("signup.html", username = username, password = password, verify=verify, email=email, error=error)

#     def get(self):
#         self.render_sign_up()


#     def post(self):
#         username = self.request.get('name')
#         password = self.request.get('password')
#         verify = self.request.get('verify')
#         user_email = self.request.get('email')
#         nameError = ""
#         passwordError = ""
#         emailError = ""

#         name = validate(nameReg, username)
#         passwordMatch = match(password, verify)
#         if passwordMatch:
#             passwordValid = validate(passwordReg, password)
#         else:
#             password = False
#         email = validate(emailReg, user_email)

#         if not (name and passwordMatch and passwordValid and email):
#             if not name:
#                 nameError = (errorLabel % {"error": {"type": "username"}})
#             if not passwordMatch:
#                 passwordError = (errorLabel % {"error": mismatchText})
#             elif not passwordValid:
#                 passwordError = (errorLabel % {"error": {"type": "password"}})
#             if not email: 
#                 emailError = (errorLabel % {"error": {"type": "email"}})
#         else:           
#             hashedPW = make_pw_hash(username, password)
#             user = Users(username = username, password = password, email = email)
#             user.put()
#             print(user.key().id())
#             new_cookie_val = make_secure_val(username)
#             self.response.headers.add_header('Set-Cookie', 'userID=%s; Path=/' % str(hashedPW))
#             print "hashedPW: %s" % str(hashedPW)
#             print "hello world"
#             self.redirect("/welcome")

class Signup(BlogHandler):
    def get(self):
        self.render("signup-form.html")

    def post(self):
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username = self.username,
                      email = self.email)

        if not valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_password(self.password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_email(self.email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('signup-form.html', **params)
        else:
            self.done()

    def done(self, *a, **kw):
        raise NotImplementedError

class Register(Signup):
    def done(self):
        #check to see if user already exists
        u = User.by_name(self.username)
        if u:
            msg = 'User with that name already exists'
            self.render('signup.html', error_username = msg)
        else: 
            u = User.register(self.username, self.password, self.email)
            u.put()

            #self.login(u)
            self.set_secure_cookie('user_id', str(user.key().id()))
            self.redirect('/welcome')

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
            
class ViewBlogPost(Handler):
    def render_blog_post(self, title="", body="", error=""):
        self.render("blogpost.html", title=title, body=body, error=error)
    
    def get(self):
        post = Blog.get_by_id(int(self.request.get("id")))
        self.render_blog_post(title=post.title, body=post.body)

class WelcomeHandler(Handler):
    def render_welcome_page(self, username=""):
        self.render("welcome.html",username=username)

    def get(self):
        #read the cookie
        user_cookie_str = self.request.cookies.get('user_id')
        #open DB
        user_id = user_cookie_str.split('|')[0]
        hashed_val = user_cookie_str.split('|')[1]
        #find user with that username
        user = db.GqlQuery("SELECT * from USERS WHERE USER_ID = %s" %user_id)        
        #use checkval against the hashed PW, get salt from hashed PW
        #----not yet----
        #hashed_pw = user.hashed_password.split('|')[0]
        #salt = user.hashed_password.split('|')[1]
        #if check_secure_val("%s + %s + %s" % (user.username + ))
        #if valid, welcome user


        user_name = self.request.get('username')
        self.render_welcome_page(username = user_name)



def users_key(group = 'default'):
    return db.Key.from_path('users', group)

def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

def validate_pw(name, password, h):
    salt = h.split('|')[0]
    return h == make_pw_hash(name, password, salt)

def hash_str(h):
    return hmac.new("secret", h).hexdigest()

#from udacity video
def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))

def make_pw_hash(name, pw):
    if not salt:
        salt = make_salt()
    hashed = hashlib.sha256(name + pw + salt).hexdigest()
    return "%s|%s" % (hashed, salt)



def match(str1, str2):
    if str1 == str2:
        return True

def validate(expression, strToVal):
        return expression.match(strToVal)


app = webapp2.WSGIApplication([('/', MainPage),
                              ('/blog/([0-9]+)', ViewBlogPost),
                              ('/newpost', NewPost),
                              ('/signup', Register),
                              ('/welcome', WelcomeHandler)], debug=True)