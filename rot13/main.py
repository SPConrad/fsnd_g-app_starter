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
import string
import jinja2
import webapp2

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

inputText = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
outputText = "NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm"

rot13Encoder = string.maketrans(inputText, outputText)

encryptedtext = ""

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    #feel free to steal these for basic tempalte rendering
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class MainPage(Handler): 
    def get(self):
        textblock = encryptedtext
        self.render("rot13form.html", )

    def post(self):
        entered_string = self.request.get('entered_string')
        newString = string.translate("Hello world", rot13Encoder)
        #encryptedtext = encryptText(entered_string)
        self.render("rot13form.html", textblock = newString)


def encryptText(textToEncrypt):
    new_s = ""
    for c in textToEncrypt:
        aVal = ord(c)
        if aVal > 79 and aVal < 91 or aVal > 110:
            aVal -= 13
        elif aVal > 64 and aVal <= 79 or aVal > 97 and aVal <= 110:
            aVal += 13

        new_s += chr(aVal)
    
    return new_s

app = webapp2.WSGIApplication([('/', MainPage)
                                ],
                                debug=True)