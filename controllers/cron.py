# coding: utf8
# try something like
def index(): return dict(message="hello from cron.py")

def email_incomplete_papers():
    if request.env.remote_addr not in ["127.0.0.1"]:
        raise HTTP(401, 'unauthorized')

    status_filter = False 
    for status_option in [PAPER_STATUS[x] for x in NEED_SUBMIT]:
        if status_filter:
            status_filter = status_filter | (db.paper.status == status_option)
        else:
            status_filter = (db.paper.status == status_option)
            
    
    papers = db(status_filter).select(db.paper.ALL)
    count = 0
    for paper in papers:
        email_list = []
        print  paper
        for person_row in db(db.paper_associations.paper == paper.id).select(db.paper_associations.person):
            email_list.append(db.auth_user[person_row.person].email)
        
        # Unlock database by running a commit
        db.commit()
        
        message = response.render('email_templates/paper_waiting_for_submission.txt', {'paper':paper})
        mail.send(to=email_list,
            subject=T("Symposium Paper Submission, Action Required"),
            message=message)
        count += 1
    return "Sent %d email(s)" % count
