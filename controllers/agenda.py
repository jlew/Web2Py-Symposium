# coding: utf8
# try something like
def index(): return dict(message="Coming Soon")

@auth.requires_membership("Symposium Admin")
def edit():
    return dict(message="Coming Soon")
