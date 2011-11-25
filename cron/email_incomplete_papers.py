status_filter = False
for status_option in [PAPER_STATUS[x] for x in NEED_SUBMIT]:
    if status_filter:
        status_filter = status_filter | (db.paper.status == status_option)
    else:
        status_filter = (db.paper.status == status_option)

papers = db(status_filter).select()
for paper in papers:
    email_list = []
    for author in paper.authors:
        email_list.append(db.auth_user[author].email)
    message = response.render('email_templates/paper_waiting_for_submission.txt', {'paper':paper})
    print message
    mail.send(to=email_list,
        subject=T("Symposium Paper Submission, Action Required"),
        message=message)
