# coding: utf8
# try something like
def index():
    db.symposium.id.represent = lambda id: A(id,_href=URL('edit',args=id))
    return dict(form=crud.select(db.symposium))

@auth.requires_membership("Symposium Admin")
def new():
    return dict(form=crud.create(db.symposium))
    
@auth.requires_membership("Symposium Admin")
def edit(): return dict(form=crud.update(db.symposium, request.args(0)))
