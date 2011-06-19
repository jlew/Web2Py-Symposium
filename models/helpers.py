# coding: utf8
def can_edit_paper(paper):
    """
    Returns true if has edit abilities on the paper
    """
    return auth.user.id in paper.authors or len(paper.authors) == 0
    
def get_symposium_visable_papers(symposium):
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
            mentors = mentors.union(papers.authors)
    return mentors
