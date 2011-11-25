# coding: utf8
# try something like
def index():
    if request.args(0):
        symposiums = db(db.symposium.sid==request.args(0)).select()
        symp = symposiums.first()

        if not symp:
            raise HTTP(404)
        session['filter'] = symp.sid

    else:
        session.flash = "Please select a symposium to view the agenda"
        redirect( URL("default", "index") )
        symposiums = db(db.symposium.sid>0).select()
        symp = False
        session['filter'] = ""

    timeblocks = symp.timeblock.select(orderby=db.timeblock.start_time)
    return dict(timeblocks=timeblocks,symp=symp)

@auth.requires_membership("Symposium Admin")
def edit():
    symp = db.symposium(request.args(0))
    if symp:
        
        papers = db(
                    (db.paper.symposium == symp.id) &
                    (db.paper.session == None)
                   ).select(
                       db.paper.id, db.paper.title, db.paper.description, db.paper.format, db.paper.category, db.paper.authors, db.paper.mentors
                   )
        
        return dict(symposium=symp, unscheduled_papers=papers)
    else:
        raise HTTP(404)

@auth.requires_membership("Symposium Admin")
def update_order():
    sess = db.session(request.vars.ses_id)
    
    if not sess or not request.vars.order:
        raise HTTP(404)
    
    new_order = request.vars.order.split(",")
    
    if len(new_order) > 0:
        for paper in sess.paper.select(db.paper.id):
            paperid = str(paper.id)
            if paperid in new_order:
                paper.update_record( session_pos=new_order.index(paperid) )

    
@auth.requires_membership("Symposium Admin")
def add_to_session():
    sess = db.session(request.vars.ses_id)
    
    if not sess:
        raise HTTP(404)
    
    curr_paper = db.paper(request.vars.paper)
    
    if not curr_paper:
        raise HTTP(404)
        
    papers = sess.paper.select()
    
    # Shift papers for placement
    paper_position = int(request.vars.position)
    for paper in papers:
        if paper.session_pos >= paper_position:
            paper.update_record(session_pos = paper.session_pos + 1)
    
    # Place paper by updating session and paper position
    curr_paper.update_record(session = sess, session_pos = paper_position)

@auth.requires_membership("Symposium Admin")
def del_from_session():
    curr_paper = db.paper(request.vars.paper)
    
    if not curr_paper:
        raise HTTP(404)
        
    curr_paper.update_record(session = None)

def view_session():
    sess = db.session(request.args(0))
    
    if not sess:
        raise HTTP(404)
        
    return dict(sess=sess)
