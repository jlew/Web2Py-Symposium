# -*- coding: utf-8 -*-
# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []

#########################################################################
# Symposium Table
#########################################################################
db.define_table('symposium',
    Field('name','string',required=True, label=T("Symposium Name")),
    Field('sid', 'string', required=True, unique=True, label=T("Easy URL")),
    Field('reg_start', 'datetime', required=True, label=T("Registration Start")),
    Field('reg_end', 'datetime', required=True, label=T("Registration End")),
    Field('event_date', 'date', required=True, label=T("Symposium Date")),
    Field('extra_info', 'text', label=T("Additional Information")),
    Field('rooms', 'list:string', label=T("Rooms"), comment=T("Room Names for scheduling, press enter to get another room.")),
    format='%(name)s: %(event_date)s'
)

#Add after created so we don't override the unique test
db.symposium.sid.requires.insert(0,IS_SLUG())

def get_next_symposium():
    """
    Returns the next upcoming symposium.
    """
    return db(db.symposium.reg_end > request.now).select(orderby=db.symposium.event_date).first()

#########################################################################
# Paper Table
#########################################################################
db.define_table('paper',
    Field('title', 'string', required=True, 
            label=T("Paper Title"), comment="*"),
            
    Field('description', 'text', required=True,
            label=T("Paper Description"), comment="* " + \
            T("A short description or abstract of the paper")),
            
    Field('paper', 'upload', label=T("Paper Upload"), autodelete=True,
          comment=T("You may upload a copy of your paper now or come back later.")),
          
    Hidden('authors', 'list:reference auth_user', label=T("Paper Authors"), required=True,
          default=[auth.user.id if auth.user else None]),
          
    Hidden('mentors', 'list:reference auth_user', label=T("Paper Mentors"), default=[]),
                     
    Field('status', 'string', requires=IS_IN_SET(PAPER_STATUS), default=PAPER_STATUS[0],
          label=T("Paper Status"), writable=False),
          
    Field('category', 'string', requires=IS_IN_SET(PAPER_CATEGORY)),
    
    Field('symposium', 'reference symposium', default=get_next_symposium(), requires=IS_VALID_SYMP()),
    
    Field('created', 'datetime', default=request.now, writable=False),
    
    Field('modified', 'datetime', default=request.now, update=request.now, writable=False),
    
    Hidden('scheduled', 'boolean', default=False),
    Hidden('schedule_room', 'integer', default=-1),
    Hidden('schedule_start', 'time'),
    Hidden('schedule_end', 'time'),
    
    format='%(title)s'
)

def paper_update(form):
    """
    Resets the paper status to 0, need to be submitted for approval
    """
    form.vars.status=PAPER_STATUS[0]
crud.settings.update_onvalidation.paper.append(paper_update)


#########################################################################
# Paper_comment Table, used to keep track of the review process
#########################################################################
db.define_table('paper_comment',
    Field('paper', db.paper, writable=False),
    Field('author', db.auth_user, default=auth.user.id if auth.user else None, writable=False),
    Field('status', 'string', requires=IS_IN_SET(PAPER_STATUS)),
    Field('created', 'datetime', default=request.now, writable=False),
    Field('comment', 'text')
    )

def paper_comment(form):
    """
    When a comment has been posted, this method is called to update
    the paper's status and email all authors that there has been an
    update on their paper's status.
    """
    # Update Paper Status
    comment = db.paper_comment(form.vars.id)
    paper = db.paper(comment.paper)
    paper.update_record(status=form.vars.status)

    # Email authors
    author_list = [db.auth_user(author).email for author in paper.authors]
    mail.send(to=author_list, subject=T("Symposium Paper Status Update"),
    message=T("""
The Paper titled "%(title)s" has just been updated.

%(author)s has just modified your paper's status.

Status: %(status)s
%(comment)s

You may manage your submissions here: %(url)s

-- Symposium Team
""") % {
    "title":paper.title,
    "author":db.auth_user._format % db.auth_user(comment.author),
    "status":comment.status,
    "comment":comment.comment,
    "url":"http://%s%s" % (request.env.http_host, URL("papers","edit"))
    })

crud.settings.create_onaccept.paper_comment.append(paper_comment)

#########################################################################
# Paper_attachment Table, used to attach additional files like
# presentation materials
#########################################################################
db.define_table('paper_attachment',
    Field('paper', db.paper, writable=False),
    Field('author', db.auth_user, default=auth.user.id if auth.user else None, writable=False),
    Field('title', 'string', required=True, label=T("Title")),
    Field('file', 'upload', required=True, requires=IS_NOT_EMPTY()),
    Field('created', 'datetime', default=request.now, writable=False),
    Field('comment', 'string', label=T("Short Comment/Description")),
    format = "%(title)s"
    )

#########################################################################
# Helper to create admin groups and accounts when the first user is
# created.  Also sets session pre-populate flag to cause the wiki-plugin
# to build its original pages
#########################################################################
def ensure_admin(form):
    """
    When a user is created for the first time, this function will
    create the admin and review groups and add the new user to thoes
    new groups.
    """
    if form.vars.id==1:
        auth.add_group(role = 'Symposium Admin')
        auth.add_group(role = 'Reviewer')
        auth.add_membership('Symposium Admin', 1)
        auth.add_membership('Reviewer', 1)
        
        # Request that plugin_wiki pre-populate pages
        session['pre-populate'] = True

auth.settings.register_onaccept=ensure_admin
