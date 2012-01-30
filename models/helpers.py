# coding: utf8
def can_edit_paper(paper):
    """
    Returns true if has edit abilities on the paper
    """
    if not auth.user:
        return False
    
    if auth.has_membership("Symposium Admin"):
        return True
    
    return auth.user.id in [x.person for x in db(db.paper_associations.paper==paper).select()]
            
def can_review_paper(paper):
    if not auth.user:
        return False

    if auth.has_membership("Symposium Admin"):
        return True
        
    reviewer_rules = db(
        (db.reviewer.reviewer == auth.user_id) &
        (db.reviewer.symposium == paper.symposium)).select()
    
    for rule in reviewer_rules:
        if rule.global_reviewer:
            return True
        elif paper.category in rule.categories:
            return True
    return False
        
    
def get_symposium_visable_papers(symposium):
    """
    Returns a list of papers that are in a visible state for
    a given symposium.
    """
    paper_request = db(db.paper.symposium==symposium).select()
    papers=[]
    for paper in paper_request:
        if paper.status in [PAPER_STATUS[x] for x in VISIBLE_STATUS]:
            papers.append(paper)
    return papers

    
def get_symposium_judges_id(symposium):
    judges = set()
    for timeblock in db(db.timeblock.symposium == symposium.id).select(db.timeblock.id):
        for sess in db(db.session.timeblock == timeblock.id).select(db.session.judges):
            if sess.judges:
                judges = judges.union(sess.judges)
    return judges
    
def get_symposium_reviewers_id(symposium):
    reviewers = []
    for reviewer in db(db.reviewer.symposium == symposium.id).select():
        reviewers.append(reviewer.reviewer)
    return reviewers

def get_public_filter():
    status_filter = False
    for status_option in [PAPER_STATUS[x] for x in VISIBLE_STATUS]:
        if status_filter:
            status_filter = status_filter | (db.paper.status == status_option)
        else:
            status_filter = (db.paper.status == status_option)
    return status_filter
    
def get_scheduled_time(paper):
    from datetime import date, datetime, time, timedelta
    the_time = paper.session.timeblock.start_time

    papers = db( (db.paper.session==paper.session.id) & (db.paper.session_pos < paper.session_pos) ).select(orderby=db.paper.session_pos)
    for paper_item in papers:
        the_time = (datetime.combine(date.today(), the_time) + timedelta(minutes=paper_item.format.duration)).time()

    return the_time.strftime(TIME_FORMAT)
    
def get_reviewer_filter(reviewer=False):
    if auth.has_membership("Symposium Admin"):
        return (db.paper.status==PAPER_STATUS[PEND_APPROVAL])
        
    if not reviewer:
        reviewer = db(db.reviewer.reviewer == auth.user_id).select()
    
    reviewer_filter = False
    for reviewer_rule in reviewer:
        if reviewer_rule.global_reviewer:
            if reviewer_filter:
                reviewer_filter = reviewer_filter | (db.paper.symposium == reviewer_rule.symposium)
            else:
                reviewer_filter = (db.paper.symposium == reviewer_rule.symposium)
        else:
            if reviewer_filter:
                reviewer_filter = reviewer_filter | (
                    (db.paper.symposium == reviewer_rule.symposium) & (db.paper.category.belongs(reviewer_rule.categories)))
            else:
                reviewer_filter = ((db.paper.symposium == reviewer_rule.symposium) & (db.paper.category.belongs(reviewer_rule.categories)))

    if reviewer_filter:
        return (db.paper.status==PAPER_STATUS[PEND_APPROVAL]) & reviewer_filter
    else:
        return False
