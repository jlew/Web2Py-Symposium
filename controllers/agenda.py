# coding: utf8
# try something like
def index():
    symp = db(db.symposium.sid==request.args(0)).select().first()
    if symp:
        #response.files.append(URL('static','week-cal/libs/css/smoothness/jquery-ui-1.8.11.custom.css'))
        #response.files.append(URL('static','week-cal/jquery.weekcalendar.css'))
        #response.files.append(URL('static','week-cal/skins/default.css'))
        #response.files.append(URL('static','week-cal/skins/gcalendar.css'))
        #response.files.append(URL('static','week-cal/jquery.weekcalendar.js'))
        papers = get_symposium_visable_papers(symp)
        import datetime
        papers.sort(key=lambda x: x.schedule_start if (x.schedule_start and x.scheduled) else datetime.time())
        return dict(symposium=symp, papers=papers)
    else:
        raise HTTP(404)

@auth.requires_membership("Symposium Admin")
def edit():
    symp = db.symposium(request.args(0))
    if symp:
        response.files.append(URL('static','week-cal/libs/css/smoothness/jquery-ui-1.8.11.custom.css'))
        response.files.append(URL('static','week-cal/jquery.weekcalendar.css'))
        response.files.append(URL('static','week-cal/skins/default.css'))
        response.files.append(URL('static','week-cal/skins/gcalendar.css'))
        response.files.append(URL('static','week-cal/jquery.weekcalendar.js'))
        return dict(symposium=symp, papers=get_symposium_visable_papers(symp))
    else:
        raise HTTP(404)
    
@auth.requires_membership("Symposium Admin")
def schedule_event():
    from datetime import time
    paper = db.paper(request.vars.id)
    symposium = paper.symposium
    paper.update_record(
        scheduled= int(request.vars.room) != len(symposium.rooms),
        schedule_start=time( int(request.vars.start_h), int(request.vars.start_m), 0),
        schedule_end=time( int(request.vars.end_h), int(request.vars.end_m), 0),
        schedule_room=int(request.vars.room)
    )
    return ""
