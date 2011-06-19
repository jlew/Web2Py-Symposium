# coding: utf8
# try something like
def index(): 
    if request.args(0):
        symposiums = db(db.symposium.sid == request.args(0)).select()
        all = False
    else:
        symposiums = db(db.symposium.id > 0).select(orderby=~db.symposium.event_date)
        all = True
    
    # Build Dict of all symposiums containing the symposium,
    # its papers, and the number of pending/non-approved papers
    ret = []
    for symposium in symposiums:
        ret.append( {"symposium": symposium,
                   "mentors": [db.auth_user(x) for x in get_symposium_mentors_id(symposium)],
                   "authors": [db.auth_user(x) for x in get_symposium_authors_id(symposium)]})

    return dict(ret=ret, all=all)

def profile(): 
    user = db.auth_user(request.args(0))
    name = db.auth_user._format % user
    return dict(name=name,
        affiliation=user.affiliation,
        profile_picture=user.profile_picture,
        short_profile = user.short_profile,
        web_page = user.web_page,
        id = user.id)
