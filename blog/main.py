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

from google.appengine.ext import db

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

# class Blog(db.Model):
#     title = db.StringProperty(required = True)
#     body = db.TextProperty(required = True)
#     created = db.DateTimeProperty(auto_now_add = True)
#     last_modified = db.DateTimeProperty(auto_now = True)

#     def render(self):
#         self._render_text = self.content.replace('\n', '<br>')
#         return render_str("blogpost.html", p = self)


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

app = webapp2.WSGIApplication([('/', MainPage),
                              ('/blog/([0-9]+)', ViewBlogPost),
                              ('/newpost', NewPost)], debug=True)