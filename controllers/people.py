# coding: utf8
# try something like
def index(): 
    if request.args(0):
        symposiums = db(db.symposium.sid == request.args(0)).select()
        if symposiums.first():
            symp = symposiums.first()
            session['filter'] = symp.sid
            all = False
        else:
            raise HTTP(404)
    else:
        symp = False
        symposiums = db(db.symposium.id > 0).select(orderby=~db.symposium.event_date)
        all = True
        session['filter'] = ""
    
    # Build Dict of all symposiums containing the symposium,
    # its papers, and the number of pending/non-approved papers
    ret = []
    for symposium in symposiums:
        ret.append( {"symposium": symposium,
                   "mentors": [db.auth_user(x) for x in get_symposium_mentors_id(symposium)],
                   "authors": [db.auth_user(x) for x in get_symposium_authors_id(symposium)]})

    return dict(ret=ret, all=all, symp=symp)

def profile():
    if request.vars.has_key("minview"):
        response.view = "people/profile_min.html"
    user = db.auth_user(request.args(0))
    name = db.auth_user._format % user
    return dict(name=name,
        affiliation=user.affiliation,
        profile_picture=user.profile_picture,
        short_profile = user.short_profile,
        web_page = user.web_page,
        email = user.email,
        id = user.id)

def search_api():
    request_filter =  (db.auth_user.id > 0)
    if request.vars.first_name:
        request_filter = request_filter & db.auth_user.first_name.contains(request.vars.first_name)
    if request.vars.last_name:
        request_filter = request_filter & db.auth_user.last_name.contains(request.vars.last_name)
    if request.vars.affiliation:
        request_filter = request_filter & db.auth_user.affiliation.contains(request.vars.affiliation)
    if request.vars.search:
        request_filter = request_filter & db.auth_user.search_name.contains(request.vars.search)

    result = db(request_filter).select(db.auth_user.id,
        db.auth_user.first_name,
        db.auth_user.last_name,
        db.auth_user.affiliation,
        db.auth_user.search_name,
        db.auth_user.profile_picture,
        orderby=(db.auth_user.first_name, db.auth_user.first_name), limitby=(0,20))
    return dict(result=result)
