# coding: utf8
# This file builds a nag box that will nag reviewers if they have papers
# to review and authors/mentors if they have papers that are in a state that
# requires the them to submit it for approval
if auth.user:
    # If we are supressing the paper warning, we want to revoke the supress
    # if they have left the paper controller or have returned to the manage my papers screen
    if session.has_key("supress_paper_warning") and (request.controller != "papers" or \
       (request.controller == "papers" and request.function == "edit" and len(request.args) == 0)):
        del session.supress_paper_warning

    # Show warnings for incomplete papers that is not the one being created
    user_papers = db(
                    (db.paper.authors.contains(auth.user.id) | db.paper.mentors.contains(auth.user.id)) &
                    (db.paper.id != session.get("supress_paper_warning", 0))
                   ).select(db.paper.id, db.paper.title, db.paper.status)
                   
    warn_status = [PAPER_STATUS[x] for x in NEED_SUBMIT]
    warn_papers = []
    for user_paper in user_papers:
        if user_paper.status in warn_status:
            warn_papers.append( user_paper )
    
    if warn_papers:
        response.notice_msg = T("The following papers are incomplete and need to be submitted for approval.")
        response.notice_msg += UL([LI(A(x.title, _href=URL('papers','edit',anchor=x.id)), " (%s)" % x.status) for x in warn_papers])
    
    # Nag reviewers that there are papers waiting for their action.
    if auth.has_membership("Reviewer"):
        review_count = db(db.paper.status == PAPER_STATUS[PEND_APPROVAL]).count()
        if review_count:
            if not response.has_key("notice_msg"):
                response.notice_msg = ""
            response.notice_msg += T("There are %d papers waiting review.") % review_count
