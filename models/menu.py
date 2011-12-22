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

response.active_symp = False

def getMenu():
    menu = [(T('Symposium List'), False, URL('default','index'), [])]
    for m_item in db(db.page.symposium==None).select():
        menu.append( (m_item.title, False, URL('default','page', args=m_item.url)))

    # If logged in, show submit and manage options
    if auth.user:
        menu.append( (T('Submit Paper'), False, URL('papers', 'submit'), []) )
        menu.append( (T('Manage My Papers'), False, URL('papers', 'edit'), []) )
    
    # Add an admin menu if in admin group
    if auth.has_membership("Symposium Admin"):
        menu += [
            (T('Admin Actions'), False, "#", [
                (T('Symposium Management'), False, URL('editsymp','index'), []),
                (T('Manage System Users'), False, URL(request.application,'plugin_useradmin','index'), []),
                (T('Edit Page Inserts'),False,URL('plugin_wiki','index'), []),
                (T('Add Global Page'), False, URL('default','add_page'), [])
            ])
        ]
    return menu

def getSympMenu():
    menu = []

    if response.active_symp:
        menu.append((T('Symposium Details'), False, URL('default','view',args=response.active_symp.sid), []))
        menu.append((T('Papers'), False, URL('papers','index', args=response.active_symp.sid), []))
        menu.append((T('People'), False, URL('people','index', args=response.active_symp.sid), []))
        menu.append((T('Agenda'), False, URL('agenda','index', args=response.active_symp.sid), []))
        for m_item in db(db.page.symposium==response.active_symp.id).select():
            menu.append( (m_item.title, False, URL('default','page', args=[m_item.symposium.sid, m_item.url])))
    return menu
