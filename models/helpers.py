# coding: utf8
def can_edit_paper(paper):
    """
    Returns true if has edit abilities on the paper
    """
    return auth.has_membership("Symposium Admin") or\
            auth.user.id in paper.authors or\
            auth.user.id in paper.mentors or\
            len(paper.authors) == 0
    
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

def get_symposium_authors_id(symposium, all=False):
    """
    Returns a set of id's of all authors for a symposium if
    the user has a paper that is public or true is passed in
    as the all argument.
    """
    authors = set()
    for papers in symposium.paper.select():
        if all or papers.status in [PAPER_STATUS[x] for x in VISIBLE_STATUS]:
            authors = authors.union(papers.authors)
    return authors
            
def get_symposium_mentors_id(symposium, all=False):
    """
    Returns a set of id's of all mentors for a symposium if
    the user is a mentor of a paper that is public or true is passed in
    as the all argument.
    """
    mentors = set()
    for papers in symposium.paper.select():
        if all or papers.status in [PAPER_STATUS[x] for x in VISIBLE_STATUS]:
            mentors = mentors.union(papers.mentors)
    return mentors
    
def get_symposium_judges_id(symposium):
    judges = set()
    for timeblock in db(db.timeblock.symposium == symposium.id).select(db.timeblock.id):
        for sess in db(db.session.timeblock == timeblock.id).select(db.session.judges):
            if sess.judges:
                judges = judges.union(sess.judges)
    return judges


def batch_cell_view(cell, paper, td_class=""):
    def link_wrap(content):
        return TD(
                  A(content,
                      _href=URL("papers","edit_cell",args=[cell,paper.id], extension="load"),
                      cid="pid_%s_%d" % (cell, paper.id),
                      _style="text-decoration: none;"),
                  _id="pid_%s_%d" % (cell, paper.id),
                  _class=td_class)

    if cell == "status":
        return link_wrap(paper.status[:6])
        
    elif cell == "title":
        return link_wrap(paper.title)
        
    elif cell=="description":
        msg = B(I(T("Short Abstract"))) if len(paper.description) < 200 else T("Abstract")
        return link_wrap( DIV( msg, SPAN(paper.description) ) )
        
    elif cell=="symposium":
        smp = db.symposium[paper.symposium]
        return link_wrap( DIV( smp.sid, SPAN(smp.name, _class="small") ) )
        
    elif cell=="category":
        return link_wrap(paper.category)
        
    elif cell=="format":
        return link_wrap(paper.format)

def get_public_filter():
    status_filter = False
    for status_option in [PAPER_STATUS[x] for x in VISIBLE_STATUS]:
        if status_filter:
            status_filter = status_filter | (db.paper.status == status_option)
        else:
            status_filter = (db.paper.status == status_option)
    return status_filter
