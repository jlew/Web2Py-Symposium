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

#Symposium list required for Symposium and paper Menus
symposiums_past = db(db.symposium.event_date < request.now.date()).select(orderby=~db.symposium.event_date)
symposiums = db(db.symposium.event_date >= request.now.date()).select(orderby=~db.symposium.event_date)

# Build agenda Menu
# TODO: Remove this agenda menu to fid the other menu style, need to rewrite agenda system to do this
current_symp = [(db.symposium._format % x, False, URL('agenda', 'index', args=x.sid), []) for x in symposiums]
past_symp = [(db.symposium._format % x, False,  URL('agenda', 'index', args=x.sid), []) for x in symposiums_past]

if past_symp:
    current_symp.append( (T("Past Symposiums"), False, "#", past_symp) )

paper_menu=[]
# If logged in, show submit and manage options
if auth.user:
    paper_menu.append( (T('Submit Paper'), False, URL('papers', 'submit'), []) )
    paper_menu.append( (T('Manage My Papers'), False, URL('papers', 'edit'), []) )

# Only want to show review option to members who can review papers
if auth.has_membership("Reviewer"):
        paper_menu += [(T('Review Papers'), False, URL('papers','review'), [])]

response.menu = [
        (T('Home'), False, URL('default','index'), []),
        (T('Papers'), False, URL('papers','index'), paper_menu),
        (T('People'), False, URL('people','index'), []),
        (T('Agenda'), False, "#", current_symp),
    ]
    
# Add an admin menu if in admin group
if auth.has_membership("Symposium Admin"):
    response.menu += [
        (T('Admin Actions'), False, "#", [
            (T('Symposium Management'), False, URL('editsymp','index'), []),
            (T('Manage System Users'), False, URL(request.application,'plugin_useradmin','index'), []),
            (T('Batch Edit Papers'), False, URL('papers','batch'), []),
            (T('Edit Pages'),False,URL('plugin_wiki','index'), []),
        ])
        ]
