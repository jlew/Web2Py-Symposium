# coding: utf8
DATE_FORMAT = "%m/%d/%y"
DATE_TIME_FORMAT = "%m/%d/%y %I:%M:%S %p"
TIME_FORMAT = "%I:%M:%S %p"

# The status the paper may take, the first one is the default status
PAPER_STATUS = (
            T("Incomplete/Not Submitted"),    #0
            T("Awaiting Approval"),           #1
            T("Approved"),                    #2
            T("Rejected/Closed/Withdrawn"),   #3
            T("Needs Revision"),              #4
        )
        
EDIT_STATUS =     [0, 1, 4]    # When the uesr is allowed to edit
NEED_SUBMIT =     [0, 4]       # When the user can to sumbit paper
VISIBLE_STATUS =  [2]          # When the paper is visible to public
PEND_APPROVAL =   1            # The waiting for approval state

PAPER_CATEGORY = (
            T('Biological and Environmental Sciences'),
            T('Chemistry and Material Science'),
            T('Physics and Astronomy'),
            T('Information, Computational, and Mathematical Sciences'),
            T('Engineering and Technology'),
            T('Humanities and Social Sciences'),
            T('Business'),
            T('Fine and Applied Arts'),
            T('Other'),
        )

PRESENTATION_FORMAT = (
            T("Lecture Presentation"),
            T("Poster Session"),
            T("Discussion Group"),
            T("Pannel Q/A"),
            T("Remote Teleconference")
        )
