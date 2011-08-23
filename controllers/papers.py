# coding: utf8
# try something like
def index():
    if request.args(0):
        symp = db(db.symposium.sid == request.args(0)).select().first()

        if not symp:
            raise HTTP(404)

        papers = db(db.paper.symposium == symp).select(orderby=(db.paper.symposium,db.paper.title))
        session['filter'] = symp.sid
        all = False
    else:
        symp = False
        papers = db(db.paper.id > 0).select(orderby=(db.paper.symposium,db.paper.title))
        session['filter'] = ""
        all = True

    ret_papers = []
    for paper in papers:
        if paper.status in [PAPER_STATUS[x] for x in VISIBLE_STATUS]:
            ret_papers.append(paper)

    return dict(papers=ret_papers, all=all, c_show_moderation = False, symp=symp)


@auth.requires_membership("Symposium Admin")
def admin_index():
    response.view = "papers/index.html"
    if request.args(0):
        symp = db(db.symposium.sid == request.args(0)).select().first()

        if not symp:
            raise HTTP(404)

        papers = db(db.paper.symposium == symp).select(orderby=(db.paper.symposium,db.paper.title))
        session['filter'] = symp.sid
        all = False
    else:
        symp = False
        papers = db(db.paper.id > 0).select(orderby=(db.paper.symposium,db.paper.title))
        session['filter'] = ""
        all = True

    ret_papers = []
    for paper in papers:
        ret_papers.append(paper)

    return dict(papers=ret_papers, all=all, c_show_moderation=True, symp=symp)

def view():
    paper = db.paper(request.args(0))

    if request.vars.has_key("minview"):
        response.view = "papers/view_min.html"

    if paper:
        if paper.status in [PAPER_STATUS[x] for x in VISIBLE_STATUS] or can_edit_paper(paper) or auth.has_membership("Reviewer"):
            return dict(paper=paper)
        else:
            raise HTTP(401, T("Paper is not public yet"))
    else:
        raise HTTP(404)
        
def abstract():
    response.view="papers/abstract.html"
    return view()

@auth.requires_login()
def submit():
    if request.vars.symp:
        valid_sym = db(
                       (db.symposium.reg_end > request.now) &
                       (db.symposium.reg_start < request.now) &
                       (db.symposium.sid == request.vars.symp)
                      ).select(orderby=db.symposium.event_date)
    else:
        valid_sym = db(
                       (db.symposium.reg_end > request.now) &
                       (db.symposium.reg_start < request.now)
                      ).select(orderby=db.symposium.event_date)

    if len(valid_sym) == 0:
        if request.vars.symp:
            raise HTTP(404, T("That id does not match an open symposium"))    
        else:
            return dict(form = T("No Symposiums open for registration"))

    elif len(valid_sym) > 1:
        choices = []
        for x in valid_sym:
            choices.append(LI(A(db.symposium._format % x, _href=URL(vars={"symp":x.sid}))))

        return dict(form = DIV(T("Select the symposium you wich to submit to."),UL(choices)))

    else:
        crud.messages.submit_button = T("Save and continue")
        db.paper.symposium.default = valid_sym.first().id
        def user_callback(form):
            session.supress_paper_warning = form.vars.id
            redirect( URL('papers','edit_members', args=form.vars.id) )

        crud.settings.create_onaccept.paper.append(user_callback)
        return dict(form=crud.create(db.paper,
                    message=T("Paper Saved, click submit for approval when complete")))

@auth.requires_login()
def edit():
    paper = db.paper(request.args(0))
    if not paper:
        response.view = "papers/managelist.html"
        papers = db(db.paper.authors.contains(auth.user.id) | db.paper.mentors.contains(auth.user.id)).select()
        return dict(papers = papers)
        
    if can_edit_paper(paper):
        db.paper.symposium.writable = False
        
        crud.messages.submit_button = T("Save and continue")

        def deleted_paper(form):
            """
            HACK/WORK AROUND FOR WEB2PY BUG
            http://www.mail-archive.com/web2py@googlegroups.com/msg42421.html
            """
            session.flash = T("Paper Deleted")
            redirect(URL('papers','edit'))

        return dict(paper=paper, form=crud.update(db.paper, request.args(0),
                             next=URL('papers','edit_members', args=paper.id),
                             ondelete=deleted_paper,
                             message=T("Paper Saved, click submit for approval when complete"),
                             deletable=auth.has_membership("Symposium Admin")))
    else:
        raise HTTP(401)
        
@auth.requires_login()
def submit_for_approval():
    paper = db.paper(request.args(0))

    if not paper:
        raise HTTP(404)

    if can_edit_paper(paper):
        db.paper_comment.paper.default = paper.id
        db.paper_comment.status.default = PAPER_STATUS[PEND_APPROVAL]
        db.paper_comment.status.writable = db.paper_comment.status.readable = False
        db.paper_comment.status.requires = IS_IN_SET( (PAPER_STATUS[PEND_APPROVAL],) )
        return dict(paper=paper, form=crud.create(db.paper_comment, next=URL('edit'),
                        message=T("Seccessfully Submitted for Review")))
    else:
        raise HTTP(401)

@auth.requires_login()
def attach_file():
    paper = db.paper(request.args(0))
    if not paper:
        raise HTTP(404)

    if can_edit_paper(paper):

        if request.args(1):
            attachment = db.paper_attachment(request.args(1))

            if attachment and attachment.paper.id == paper.id:
                return dict(paper=paper, form=crud.update(db.paper_attachment, request.args(1), next=URL('edit'),
                                            message=T("Attachment Updated")))
            else:
                raise HTTP(404)
        else:
            db.paper_attachment.paper.default = paper.id
            return dict(paper=paper, form=crud.create(db.paper_attachment, next=URL('edit'),
                                            message=T("Attachment Sucessful")))
    else:
        raise HTTP(401)

@auth.requires_membership("Reviewer")
def review():
    paper = db.paper(request.args(0))
    if paper:
        db.paper_comment.paper.default = paper.id
        db.paper_comment.status.default = paper.status
        db.paper_comment.status.label = T("Next Status")
        return dict(paper=paper, form=crud.create(db.paper_comment, next=URL('abstract',args=paper.id), message=T("Paper status updated")))
    else:
        response.view = "papers/review_list.html"
        return dict(papers=db(db.paper.status==PAPER_STATUS[PEND_APPROVAL]).select())

@auth.requires_login()      
def edit_members():
    paper =db.paper(request.args(0))
    if not paper:
        raise HTTP(404)

    if can_edit_paper(paper):
        return dict(paper=paper)
    else:
        raise HTTP(401)

@auth.requires_login()
def add_by_id():
    paper = db.paper(request.args(0))
    usr = db.auth_user(request.args(2))

    if not paper or not usr:
        raise HTTP(404)

    if can_edit_paper(paper):

        if request.args(1) == "A":
            if not usr.id in paper.authors:
                paper.authors.append(usr.id)
                paper.update_record(authors=paper.authors)
            session.s_val = request.vars.s
            session.flash=T("Author Added")
        elif request.args(1) == "M":
            if not usr.id in paper.mentors:
                paper.mentors.append(usr.id)
                paper.update_record(mentors=paper.mentors)
            session.s_val = request.vars.s
            session.flash=T("Mentor Added")
        else:
            raise HTTP(400)

        redirect( URL("papers","edit_members", args=paper.id))

    else:
        raise HTTP(401)

@auth.requires_login()
def rem_by_id():
    paper = db.paper(request.args(0))
    usr = db.auth_user(request.args(2))

    if not paper or not usr:
        raise HTTP(404)

    if can_edit_paper(paper):

        if request.args(1) == "A":
            if usr.id in paper.authors:
                paper.authors.remove(usr.id)
                if len(paper.authors) == 0:
                    session.flash = T("You can not remove the only author.")
                else:
                    paper.update_record(authors=paper.authors)
                    session.flash=T("Author Removed")
        elif request.args(1) == "M":
            if usr.id in paper.mentors:
                paper.mentors.remove(usr.id)
                paper.update_record(mentors=paper.mentors)
            session.flash=T("Mentor Removed")
        else:
            raise HTTP(400)

        redirect( URL("papers","edit_members", args=paper.id))

    else:
        raise HTTP(401)

@auth.requires_login()     
def register_user():
    paper = db.paper(request.args(0))
    if not can_edit_paper(paper):
        raise HTTP(401)
    
    if not paper:
        raise HTTP(404, T("Paper not found"))
        
    if request.args(1) not in ["A","M"]:
        raise HTTP(404, T("Author/Mentor Not Defined"))

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

        if request.args(1) == "A":
            paper.authors.append( user.id )
            paper.update_record(authors=paper.authors)
        else:
            paper.mentors.append( user.id )
            paper.update_record(mentors=paper.mentors)

        mail.send(to=user.email, subject=T("Symposium Registration System: You have been registered"),
              message=T("""
Dear %(name)s,

%(user)s <%(user_email)s> has registered an account for you so that
they may add you as an %(type)s for the paper titled %(title)s.

Your Account Details:
Email: %(email)s
Random Generated Password: %(password)s

You may view and update your account profile here: %(url)s

Your papers can be viewed and managed here: %(manage_paper_url)s
""") % {
        "name": db.auth_user._format % user,
        "user": db.auth_user._format % auth.user,
        "user_email": auth.user.email,
        "email": user.email,
        "password": the_pass,
        "url":"http://%s%s" % (request.env.http_host, URL("default","user",args="profile")),
        "manage_paper_url":"http://%s%s" % (request.env.http_host, URL("papers","edit")),
        "type": T("Author") if request.args(1) == "A" else T("Mentor"),
        "title": paper.title,
        })
    
    crud.settings.create_onaccept.auth_user.insert(0, user_callback)
    return dict(title=T("Author") if request.args(1) == "A" else T("Mentor"),
                form=crud.create(db.auth_user, message=T("Account created and linked to paper")))
                
@auth.requires_membership("Symposium Admin")
def batch():
    papers = db(db.paper.id>0).select()
    return dict(papers=papers)

@auth.requires_membership("Symposium Admin")
def edit_cell():
    paper = db.paper[request.args(1)]
    if not paper:
        raise HTTP(404)
        
    if request.vars.has_key("return"):
        return dict(msg=batch_cell_view(request.args(0), paper))
        
    form = SQLFORM(db.paper, paper, fields=[request.args(0)], showid=False, ignore_rw=True,
                   labels={request.args(0):""}, formstyle="divs", comments=False)
    if form.accepts(request.vars, session):
        return dict(msg=batch_cell_view(request.args(0), db.paper[request.args(1)]))
    return dict(form=DIV(form,A(
                            T("Cancel"),
                            _href=URL(args=request.args, vars={"return":True}), cid="pid_%s_%d" % (request.args(0), paper.id),
                            _style="position: absolute; bottom: 3px; left: 80px;"
                            ), _style="position: relative;"))
