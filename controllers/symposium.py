# coding: utf8
# try something like
def index(): return dict(message="hello from symposium.py")

@auth.requires_login()
def attend():
    symp = db(db.symposium.sid == request.args(0)).select().first()
    
    if not symp:
        raise HTTP(404)
        
    if symp.reg_end < request.now:
        session.flash = T("Registraiton Period is Over")
        redirect( URL("default","index") )
    
    if symp.reg_start > request.now:
        session.flash = T("This symposium has not started to accept registrations")
        redirect( URL("default","index") )
        
    if auth.user.id in (symp.attendees or []):
        session.flash = T("You are already attending this symposium")
        redirect( URL("default","index") )
    
    else:
        if symp.attendees:
            symp.attendees.append( auth.user.id )
        else:
            symp.attendees = [auth.user.id]
        symp.update_record(attendees=symp.attendees)
        
        session.flash = T("You have been registered for the symposium")
        redirect( URL("default","index") )
