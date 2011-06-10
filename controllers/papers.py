# coding: utf8
# try something like
def index():
    symposium = db(db.symposium.sid==request.args(0)).select().first()
    paper_request = db(db.paper.symposium==symposium).select()
    papers=[]
    pending = 0
    for paper in paper_request:
        if paper.status in [PAPER_STATUS[x] for x in VISIBLE_STATUS]:
            papers.append(paper)
        else:
            pending += 1


    return dict(papers=papers, pending=pending, symposium=symposium)

@auth.requires_login()
def submit(): return dict(form=crud.create(db.paper))

@auth.requires_login()
def edit():
    paper = db.paper(request.args(0))
    if not paper:
        response.view = "papers/managelist.html"
        papers = db(db.paper.authors.contains(auth.user.id)).select()
        return dict(papers = papers)
    
    
        #db.paper.id.represent = lambda id: A(id,_href=URL('edit',args=id))
        #return dict(form=crud.select(db.paper, query=db.paper.authors.contains(auth.user.id)))
        
    if can_edit_paper(paper):
        db.paper.symposium.writable = False
        
        return dict(form=crud.update(db.paper, request.args(0), next=URL('papers','edit')))
    else:
        raise HTTP(401)
        
@auth.requires_login()
def submit_for_approval():
    paper = db.paper(request.args(0))
    if can_edit_paper(paper):
        paper.update_record(status = PAPER_STATUS[PEND_APPROVAL])
        session.flash = T("Paper submitted for moderation")
        redirect( URL("edit") )
    else:
        raise HTTP(401)


#TODO ADD REQUIRED ROLE OF MODERATOR
@auth.requires_login()
def review():
    paper = db.paper(request.args(0))
    if paper:
        db.paper_comment.paper.default = paper.id
        db.paper_comment.status.default = paper.status
        return dict(paper=paper, form=crud.create(db.paper_comment, next=URL('review')))
    else:
        response.view = "papers/review_list.html"
        return dict(papers=db(db.paper.status==PAPER_STATUS[PEND_APPROVAL]).select())
