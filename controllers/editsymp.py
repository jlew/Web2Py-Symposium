# coding: utf8
# try something like
@auth.requires_membership("Symposium Admin")
def index():
    redirect( URL('default','index') )

@auth.requires_membership("Symposium Admin")
def new():
    return dict(form=crud.create(db.symposium, next=URL("editsymp","close_parent")))
    
@auth.requires_membership("Symposium Admin")
def edit():
    return dict(form=crud.update(db.symposium, request.args(0), next=URL("editsymp","close_parent")))

@auth.requires_membership("Symposium Admin")
def create_timeblock():
    symp = db.symposium( request.args(0) )
    
    if not symp:
        raise HTTP(404)
    
    db.timeblock.symposium.default = symp.id
    return dict( form=crud.create(db.timeblock, next=URL("editsymp","close_parent")))
        
@auth.requires_membership("Symposium Admin")
def edit_timeblock():
    timeblock = db.timeblock(request.args(0))
    
    if not timeblock:
        raise HTTP(404) 
    
    # This allows us to clear links as the sessions will be deleted
    sess_list = timeblock.session.select()
    def clearLinks(t):
        for sess in sess_list:
            for paper in sess.paper.select():
                paper.update_record(session=None)

    return dict(form=crud.update(db.timeblock, timeblock, ondelete=clearLinks, next=URL("editsymp","close_parent")))
    
@auth.requires_membership("Symposium Admin")
def create_room():
    symp = db.symposium( request.args(0) )
    
    if not symp:
        raise HTTP(404)
        
    db.room.symposium.default = symp.id
    return dict(form=crud.create(db.room, next=URL("editsymp","close_parent")))
        
@auth.requires_membership("Symposium Admin")
def edit_room():
    room = db.room(request.args(0))
    
    if not room:
        raise HTTP(404) 
        
        # This allows us to clear links as the sessions will be deleted
    sess_list = room.session.select()
    def clearLinks(t):
        for sess in sess_list:
            for paper in sess.paper.select():
                paper.update_record(session=None)

    return dict(form=crud.update(db.room, room, ondelete=clearLinks, next=URL("editsymp","close_parent")))

@auth.requires_membership("Symposium Admin")
def edit_session():
    sess = db.session(request.args(0))
    
    if not sess:
        raise HTTP(404)
        
    symp = sess.timeblock.symposium
    
    def clearLinks(form):
        for paper in sess.paper.select():
            paper.update_record(session=None)

    db.session.room.requires = IS_IN_DB(db(db.room.symposium==symp.id),db.room.id,"%(name)s")
    db.session.timeblock.requires = IS_IN_DB(db(db.timeblock.symposium==symp.id),db.timeblock.id,"%(start_time)s")
    return dict(form=crud.update(db.session, sess, next=URL("editsymp","close_parent"), ondelete=clearLinks), symp=sess.timeblock.symposium)
    

@auth.requires_membership("Symposium Admin")
def create_session():
    symp = db.symposium(request.args(0))
    room = db.room(request.args(1))
    timeb = db.timeblock(request.args(2))
    
    if not (symp and room and timeb):
        raise HTTP(404)
    
    db.session.room.requires = IS_IN_DB(db(db.room.symposium==symp.id),db.room.id,"%(name)s")
    db.session.timeblock.requires = IS_IN_DB(db(db.timeblock.symposium==symp.id),db.timeblock.id,"%(start_time)s")
    db.session.room.default = room.id
    db.session.timeblock.default = timeb.id
    return dict(form=crud.create(db.session, next=URL("editsymp","close_parent")))
    
def close_parent():
    return dict()

@auth.requires_membership("Symposium Admin")
def edit_session_judges():
    sess = db.session(request.args(0))
    
    if not sess:
        raise HTTP(404)
        
    return dict(sess=sess)
    
@auth.requires_membership("Symposium Admin")
def add_judge_by_id():
    sess = db.session(request.args(0))
    usr = db.auth_user(request.args(1))

    if not sess or not usr:
        raise HTTP(404)

    if not usr.id in sess.judges:
        sess.judges.append(usr.id)
        sess.update_record(judges=sess.judges)
        session.s_val = request.vars.s
        session.flash=T("Judge Added")

        redirect( URL("editsymp","edit_session_judges", args=sess.id))

    else:
        raise HTTP(401)
        
@auth.requires_membership("Symposium Admin")      
def rem_judge_by_id():
    sess = db.session(request.args(0))
    usr = db.auth_user(request.args(1))

    if not sess or not usr:
        raise HTTP(404)

    if usr.id in sess.judges:
        sess.judges.remove(usr.id)
        sess.update_record(judges=sess.judges)
        session.flash=T("Judge Removed")
        
        redirect( URL("editsymp","edit_session_judges", args=sess.id))

    else:
        raise HTTP(401)
        
@auth.requires_membership("Symposium Admin")       
def register_judge():
    sess = db.session(request.args(0))
    
    if not sess:
        raise HTTP(404)

    # Generate a password for the new user
    from hashlib import sha1
    the_pass = sha1(str(request.now)).hexdigest()[10:20]
    db.auth_user.password.default,throw_away=db.auth_user.password.validate(the_pass)
    db.auth_user.password.writable=db.auth_user.password.readable=False
    
    # Lets keep track of who added the user
    db.auth_user.registered_by.default=auth.user.id
    
    # Hide profile info to allow user to fill in at a later time
    db.auth_user.profile_picture.writable=db.auth_user.profile_picture.readable=False
    db.auth_user.mobile_number.writable=db.auth_user.mobile_number.readable=False
    db.auth_user.web_page.writable=db.auth_user.web_page.readable=False
    db.auth_user.short_profile.readable=db.auth_user.short_profile.writable=False

    # Lets handle the new user
    def user_callback(form):
        user = db.auth_user(form.vars.id)

        sess.judges.append( user.id )

        mail.send(to=user.email, subject=T("Symposium Registration System: You have been registered"),
              message=T("""
Dear %(name)s,

%(user)s <%(user_email)s> has registered an account for you so that
they may add you as a judge.

Your Account Details:
Email: %(email)s
Random Generated Password: %(password)s

You may view and update your account profile here: %(url)s

""") % {
        "name": db.auth_user._format % user,
        "user": db.auth_user._format % auth.user,
        "user_email": auth.user.email,
        "email": user.email,
        "password": the_pass,
        "url":"http://%s%s" % (request.env.http_host, URL("default","user",args="profile")),
        })
    
    crud.settings.create_onaccept.auth_user.insert(0, user_callback)
    return dict(form=crud.create(db.auth_user, message=T("Account created and linked to session")))

@auth.requires_membership("Symposium Admin")
def email():
    symposium = db.symposium(request.args(0))
    if not symposium:
        raise HTTP404(T("Symposium Not Found"))
        
    form = SQLFORM.factory(
        Field('subject', 'string', label=T("Subject"), requires=IS_NOT_EMPTY()),
        Field('message', 'text', label=T("Message"), requires=IS_NOT_EMPTY()),
        Field('who', default=[T("Authors")],
            requires=IS_IN_SET((T("Authors"),T("Mentors"),T("Judges")),multiple=True),
            widget=SQLFORM.widgets.checkboxes.widget
        ))
        
    if form.accepts(request.vars, session):
        users = set()
        if T("Authors") in form.vars.who:
            users = users.union(get_symposium_authors_id(symposium, True))
        
        if T("Mentors") in form.vars.who:
            users = users.union(get_symposium_mentors_id(symposium, True))
            
        if T("Judges") in form.vars.who:
            users = users.union(get_symposium_judges_id(symposium))
    
        emails = [db.auth_user(u).email for u in users]
        
        mail.send(reply_to=auth.user.email,
                  to=auth.user.email,
                  bcc=emails,
                  subject=form.vars.subject,
                  message=form.vars.message + "\n\n\n" +
                          T("This message was sent on behalf of %(name)s for your involvment in %(symp_name)s: %(symp_date)s") %
                              {
                              "name": db.auth_user._format % auth.user,
                              "symp_name": symposium.name,
                              "symp_date": symposium.event_date.strftime(DATE_FORMAT)
                              }
                          )
        response.flash = 'Email Sent'
        
    elif form.errors:
        response.flash = 'form has errors'
    return dict(form=form)
