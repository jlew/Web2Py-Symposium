# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.title = request.application
response.subtitle = T('customize me!')

#http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'you'
response.meta.description = 'Free and open source full-stack enterprise framework for agile development of fast, scalable, secure and portable database-driven web-based applications. Written and programmable in Python'
response.meta.keywords = 'web2py, python, framework'
response.meta.generator = 'Web2py Enterprise Framework'
response.meta.copyright = 'Copyright 2007-2010'


symp_list = [(db.symposium._format % x, False, URL('papers', 'index', args=x.sid), []) for x in db(db.symposium.id > 0).select(orderby=db.symposium.event_date)]

response.menu = [
    (T('Home'), False, URL('default','index'), []),
    (T('Papers'), False, "#", [
        (T('View Papers'), False, URL('papers', 'index'), symp_list),
        (T('Submit Paper'), False, URL('papers', 'submit'), []),
        (T('Manage My Papers'), False, URL('papers', 'edit'), []),
        (T('Review Papers'), False, URL('papers','review'), []),
    ]),
    ]
    
if auth.has_membership("Symposium Admin"):
    response.menu += [
        (T('Symposium Management'), False, "#", [
            (T('Edit Symposiums'), False, URL('editsymp','index'), []),
            (T('New Symposium'), False, URL('editsymp','new'), []),
        ])]
    response.menu.append((T('Manage System Users'), False, URL(request.application,'plugin_useradmin','index'), []))
