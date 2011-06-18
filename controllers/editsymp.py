# coding: utf8
# try something like
@auth.requires_membership("Symposium Admin")
def index():
    return dict(symposiums=db(db.symposium.id>0).select(orderby=~db.symposium.event_date))

@auth.requires_membership("Symposium Admin")
def new():
    return dict(form=crud.create(db.symposium, next=URL("editsymp","index")))
    
@auth.requires_membership("Symposium Admin")
def edit(): return dict(form=crud.update(db.symposium, request.args(0), next=URL("editsymp","index")))

@auth.requires_membership("Symposium Admin")
def email():
    symposium = db.symposium(request.args(0))
    if not symposium:
        raise HTTP404(T("Symposium Not Found"))
        
    form = SQLFORM.factory(
        Field('subject', 'string', label=T("Subject"), requires=IS_NOT_EMPTY()),
        Field('message', 'text', label=T("Message"), requires=IS_NOT_EMPTY()),
        Field('who', default=[T("Authors")], requires=IS_IN_SET((T("Authors"),T("Mentors")),multiple=True)))
        
    if form.accepts(request.vars, session):
        users = set()
        if T("Authors") in form.vars.who:
            users = users.union(get_symposium_authors_id(symposium, True))
        
        if T("Mentors") in form.vars.who:
            users = users.union(get_symposium_mentors_id(symposium, True))
    
        emails = [db.auth_user(u).email for u in users]
        emails.append(auth.user.email) #make sure the sender gets a copy of the email
        
        mail.send(reply_to=auth.user.email,
                  to=emails,
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
