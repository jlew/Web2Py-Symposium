# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.title = request.application
response.subtitle = T('customize me!')

#http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Justin Lewis <jlew.blackout@gmail.com>'
response.meta.description = 'Symposium registration system written in the Python Web2py framework.'
response.meta.keywords = 'Symposium, Conference'
response.meta.generator = 'Web2py Enterprise Framework'
response.meta.copyright = 'Copyright 2011'


symposiums = db(db.symposium.id > 0).select(orderby=~db.symposium.event_date)

paper_symp_list = [(db.symposium._format % x, False,
                URL('papers', 'index', args=x.sid), []) for x in symposiums]
symp_list =  [(db.symposium._format % x, False,
                URL('papers', 'index', args=x.sid), [
                    (T('View Participants'), False, URL('people', 'index', args=x.sid), []),
                    (T('View Agenda'), False, URL('agenda', 'index', args=x.sid), []),
                    (T('View Papers'), False, URL('papers', 'index', args=x.sid), []),
                ]) for x in symposiums]

response.menu = [
    (T('Home'), False, URL('default','index'), []),
    (T('Symposiums'), False, "#", symp_list),
    (T('Papers'), False, "#", [
        (T('View Papers'), False, URL('papers', 'index'), paper_symp_list),
        (T('Submit Paper'), False, URL('papers', 'submit'), []),
        (T('Manage My Papers'), False, URL('papers', 'edit'), []),
        (T('Review Papers'), False, URL('papers','review'), []),
    ]),
    ]
    
if auth.has_membership("Symposium Admin"):
    response.menu += [
        (T('Admin Actions'), False, "#", [
            (T('Symposium Management'), False, URL('editsymp','index'), []),
            (T('Manage System Users'), False, URL(request.application,'plugin_useradmin','index'), []),
            (T('Edit Pages'),False,URL('plugin_wiki','index'))
        ])
        ]
