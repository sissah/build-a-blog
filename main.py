#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
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
#
import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        h = jinja_env.get_template(template)
        return h.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Opinion(db.Model):
    title = db.StringProperty(required = True)
    elaboration = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class Signup(Handler):
    def get(self):
        self.response.write("Type /blog into the url!")

class ViewPostHandler(Handler):
    def render_post(self, title="", elaboration="", error=""):
        self.render("front.html", title=title, elaboration=elaboration, error=error)
    def get(self, id):
        t = Opinion.get_by_id(int(id))
        post_title=t.title
        post_elaboration= t.elaboration
        self.render("singlepost.html", title=post_title, elaboration=post_elaboration)



class MainPage(Handler):
    def render_new(self, title="", elaboration="", error=""):
        opinions = db.GqlQuery("SELECT * FROM Opinion "
                            "ORDER BY created DESC "
                            "LIMIT 5")
        self.render("front.html", title=title, elaboration=elaboration, error=error, opinions=opinions)

    def get(self):
        self.render_new()

class NewEntry(Handler):
    def render_post(self, title="", elaboration="", error=""):
        self.render("newpost.html", title=title, elaboration=elaboration, error=error)
    def get(self):
        self.render_post()
    def post(self):
        title = self.request.get("title")
        elaboration = self.request.get("elaboration")

        if title and elaboration:
            e = Opinion(title = title, elaboration = elaboration)
            e.put()

            self.redirect("/blog")
        else:
            error = "To submit a post, you need to include both a title and body."
            self.render_post(title=title, elaboration=elaboration, error=error)
app = webapp2.WSGIApplication([
    ('/blog', MainPage),('/blog/newpost', NewEntry),('/',Signup), webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
