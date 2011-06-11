# coding: utf8
# try something like
def index(): 
    if request.args(0):
        symposiums=db(db.symposium.sid==request.args(0)).select()
    else:
        symposiums=db(db.symposium.id>0).select()
    
    authors = set()
    mentors = set()
    for symposium in symposiums:
        for papers in symposium.paper.select():
            authors = authors.union(papers.authors)
            mentors = mentors.union(papers.mentors)
    if len(symposiums) == 1:
        p_title = T("Participants from %s" % (db.symposium._format % symposiums.first()))
    else:
        p_title = T("Participants")
        
    authors=[db.auth_user(x) for x in authors]
    authors.sort(key = lambda x: db.auth_user._format % x)
    
    mentors=[db.auth_user(x) for x in mentors]
    mentors.sort(key = lambda x: db.auth_user._format % x)
    
    return dict(p_title=p_title,
                authors=authors,
                mentors=mentors
                )

def profile(): 
    user = db.auth_user(request.args(0))
    name = db.auth_user._format % user
    return dict(name=name,
        affiliation=user.affiliation,
        profile_picture=user.profile_picture,
        short_profile = user.short_profile,
        web_page = user.web_page,
        id = user.id)
