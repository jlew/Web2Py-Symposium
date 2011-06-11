# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html
    """
    return dict(symposiums=db(db.symposium.id>0).select(orderby=~db.symposium.event_date))

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    del response.headers['Cache-Control']
    del response.headers['Pragma']
    del response.headers['Expires']
    response.headers['Cache-Control'] = "max-age=3600"
    return response.download(request,db)

def thumb():
    if not request.args(2):
        raise HTTP(404, "Image Not Found")
    del response.headers['Cache-Control']
    del response.headers['Pragma']
    del response.headers['Expires']
    response.headers['Cache-Control'] = "max-age=3600"

    import os.path
    import gluon.contenttype as c
    try:
        size_x = int(request.args(0))
        size_y = int(request.args(1))
    except:
        raise HTTP(400, "Invalid Image Dementions")
        
        
    request_path = os.path.join(request.folder, 'uploads','thumb', "%d_%d_%s" % (size_x, size_y, request.args(2)))
    request_sorce_path = os.path.join(request.folder, 'uploads', request.args(2))
    
    if os.path.exists(request_path):
        response.headers['Content-Type'] = c.contenttype(request_path) 
        return response.stream(open(request_path, 'rb'))
    
    elif os.path.exists(request_sorce_path):
        import Image
        thumb = Image.open(request_sorce_path)
        thumb.thumbnail((size_x,size_y), Image.ANTIALIAS)
        try:
            thumb.save(request_path)
        except KeyError:
            thumb.save(request_path, "JPEG")
        
        response.headers['Content-Type'] = c.contenttype(request_path) 
        return response.stream(open(request_path, 'rb'))
    else:
        raise HTTP(404, "Image not found")
