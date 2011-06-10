# coding: utf8
# try something like
def index(): return dict(form=crud.select(db.paper, query=db.paper.symposium==db(db.symposium.sid==request.args(0)).select().first()))

@auth.requires_login()
def submit(): return dict(form=crud.create(db.paper))

@auth.requires_login()
def edit():
    paper = db.paper(request.args(0))
    if not paper:
        db.paper.id.represent = lambda id: A(id,_href=URL('edit',args=id))
        return dict(form=crud.select(db.paper, query=db.paper.authors.contains(auth.user.id)))
        
    if auth.user.id in paper.authors or len(paper.authors) == 0:
        db.paper.symposium.writable = False
        
        return dict(form=crud.update(db.paper, request.args(0), next=URL()))
    else:
        raise HTTP(401)

#TODO ADD REQUIRED ROLE OF MODERATOR
@auth.requires_login()
def comment():
    paper = db.paper(request.args(0))
    db.paper_comment.paper.default = paper.id
    db.paper_comment.status.default = paper.status
    return dict(form=crud.create(db.paper_comment, next=URL()))
