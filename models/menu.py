# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.title = request.application
response.subtitle = T('Registration System')

#http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Justin Lewis <jlew.blackout@gmail.com>'
response.meta.description = 'Symposium registration system written in the Python Web2py framework.'
response.meta.keywords = 'Symposium, Conference'
response.meta.generator = 'Web2py Enterprise Framework'
response.meta.copyright = 'Copyright 2011'

paper_menu=[]
# If logged in, show submit and manage options
if auth.user:
    paper_menu.append( (T('Submit Paper'), False, URL('papers', 'submit'), []) )
    paper_menu.append( (T('Manage My Papers'), False, URL('papers', 'edit'), []) )

# Only want to show review option to members who can review papers
if auth.has_membership("Reviewer"):
        paper_menu += [(T('Review Papers'), False, URL('papers','review'), [])]

def build_menu():
    response.menu = [
        (T('Home'), False, URL('default','index'), []),
        (T('Papers'), False, URL('papers','index', args=session.get('filter', "")), paper_menu),
        (T('People'), False, URL('people','index', args=session.get('filter', "")), []),
        (T('Agenda'), False, URL('agenda','index', args=session.get('filter', "")), []),
    ]
    
    # Add an admin menu if in admin group
    if auth.has_membership("Symposium Admin"):
        response.menu += [
            (T('Admin Actions'), False, "#", [
                (T('Manage System Users'), False, URL(request.application,'plugin_useradmin','index'), []),
                (T('Batch Edit Papers'), False, URL('papers','batch'), []),
                (T('Edit Pages'),False,URL('plugin_wiki','index'), []),
            ])
            ]

build_menu()
