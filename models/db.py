# -*- coding: utf-8 -*-
PAPER_STATUS = (
            T("Awaiting Approval"),           #0
            T("Approved"),                    #1
            T("Rejected/Closed/Withdrawn"),   #2
            T("Needs Revision"),              #3
        )
        
EDIT_STATUS =     [0, 3]       # When the uesr is allowed to edit
VISIBLE_STATUS =  [1]          # When the paper is visible to public
        
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

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
#########################################################################

if request.env.web2py_runtime_gae:            # if running on Google App Engine
    db = DAL('google:datastore')              # connect to Google BigTable
                                              # optional DAL('gae://namespace')
    session.connect(request, response, db = db) # and store sessions and tickets there
    ### or use the following lines to store sessions in Memcache
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
else:                                         # else use a normal relational database
    db = DAL('sqlite://storage.sqlite')       # if not, use SQLite or other DB

# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Mail, Auth, Crud, Service, PluginManager, prettydate
mail = Mail()                                  # mailer
auth = Auth(db)                                # authentication/authorization
crud = Crud(db)                                # for CRUD helpers using auth
service = Service()                            # for json, xml, jsonrpc, xmlrpc, amfrpc
plugins = PluginManager()                      # for configuring plugins

mail.settings.server = 'logging' or 'smtp.gmail.com:587'  # your SMTP server
mail.settings.sender = 'you@gmail.com'         # your email
mail.settings.login = 'username:password'      # your credentials or None




def Hidden(*a,**b):
    b['writable']=b['readable']=False
    return Field(*a,**b)
    
fields=[
    Field('first_name', length=512,default='',comment='*'),
    Field('last_name', length=512,default='',comment='*'),
    Field('affiliation', length=512, label='Affiliation/Title',
           default="Rochester Institute of Technology, Student", required=True),
    Field('email', length=512,default='',comment='*',
          requires=(IS_EMAIL(),IS_NOT_IN_DB(db,'auth_user.email'))),
    Field('password', 'password', readable=False, label='Password',
          requires=[CRYPT(auth.settings.hmac_key)]),
    Field('web_page',requires=IS_EMPTY_OR(IS_URL())),
    Field('mobile_number',default=''),    
    Field('short_profile','text',default=''),
    Field('profile_picture','upload'),
    Hidden('registered_by','integer',default=0), #nobody
    Hidden('registration_id', length=512,default=''),
    Hidden('registration_key', length=512,default=''),
    Hidden('reset_password_key', length=512,default='',
          label=auth.messages.label_reset_password_key),
    ]

db.define_table('auth_user',
                format='%(last_name)s, %(first_name)s: %(affiliation)s',
                *fields
                )


auth.settings.create_user_groups = False
auth.settings.hmac_key = 'sha512:5ae2aa9b-4cec-4988-b114-3106591f1f15'   # before define_tables()
auth.define_tables()                           # creates all needed tables
auth.settings.mailer = mail                    # for user email verification
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.messages.verify_email = 'Click on the link http://'+request.env.http_host+URL('default','user',args=['verify_email'])+'/%(key)s to verify your email'
auth.settings.reset_password_requires_verification = True
auth.messages.reset_password = 'Click on the link http://'+request.env.http_host+URL('default','user',args=['reset_password'])+'/%(key)s to reset your password'

#########################################################################
## If you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, uncomment and customize following
# from gluon.contrib.login_methods.rpx_account import RPXAccount
# auth.settings.actions_disabled = \
#    ['register','change_password','request_reset_password']
# auth.settings.login_form = RPXAccount(request, api_key='...',domain='...',
#    url = "http://localhost:8000/%s/default/user/login" % request.application)
## other login methods are in gluon/contrib/login_methods
#########################################################################

crud.settings.auth = None        # =auth to enforce authorization on crud








#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################
db.define_table('symposium',
    Field('name','string',required=True, label=T("Symposium Name")),
    Field('sid', 'string', required=True, unique=True, label=T("Easy URL"), requires=IS_SLUG()),
    Field('reg_start', 'date', required=True, label=T("Registration Start")),
    Field('reg_end', 'date', required=True, label=T("Registration End")),
    Field('event_date', 'date', required=True, label=T("Symposium Date")),
    format='%(name)s: %(event_date)s'
)

def get_next_symposium():
    return db(db.symposium.reg_end > request.now).select(orderby=db.symposium.event_date).first()


class IS_VALID_SYMP(object):
    def __init__(self, error_message='This Symposium is not or no longer accepting registrations'):
        self.error_message = error_message
        self.multiple=False
        
    def __call__(self, value):
        try:
            print value
            if db(db.symposium.id == value).select().first():
            # Check if a valid opbject, this will allow old reg to work but not add new ones    
            #if value.reg_end > request.now and value.reg_start < request.now:
                return (value, None)

            else:
                return (value, self.error_message)

        except:
            return (value, self.error_message)
            
    def options(self):
        return [(x.id, "%s (%s)" % (x.name, x.event_date))
            for x in db(db.symposium.reg_end > request.now).select(orderby=db.symposium.event_date)]
        
    def formatter(self, value):
        v = db.symposium(value)
        if v:
            return db.symposium._format % v
        else:
            "NONE"
   
db.define_table('paper',
    Field('title', 'string', required=True, label=T("Paper Title"),
          comment=T("The title of your paper")),
    Field('description', 'text', required=True, label=T("Paper Description"),
          comment=T("A short description or abstract of the paper")),
    Field('paper', 'upload', label=T("Paper Upload"),
          comment=T("You may upload a copy of your paper now or come back later.")),
    Field('authors', 'list:reference auth_user', label=T("Paper Authors"),
          comment=T("Please check all authors of the paper. If they do not have an account, you may come back and add them later."), default=[auth.user.id if auth.user else None]),
    Field('mentors', 'list:reference auth_user', label=T("Paper Mentors"), default=[]),
    Field('status', 'string', requires=IS_IN_SET(PAPER_STATUS),default=PAPER_STATUS[0], label=T("Paper Status"), writable=False),
    Field('category', 'string', requires=IS_IN_SET(PAPER_CATEGORY)),
    Field('collage', label="College",
           requires=IS_IN_SET(
               ('CMS- Center of Multidisciplinary Studies',
                'USP- University Studies Program',
                'CAST- College of Applied Science & Technology',
                'GCCIS-Golisano College of Computing and Information Sciences',
                'CIAS- College of Imaging Arts& Sciences',
                'COLA-College of Liberal Arts',
                'COS- College of Science',
                'NTID-National Technical Institute of the Deaf',
                'KGCOE- Kate Gleason College of Engineering',
                'SCOB- Saunders College of Business',
                'GIS- Golisano Institute for Sustainability'
               ),multiple=True)),
    Field('symposium', 'reference symposium', default=get_next_symposium(), requires=IS_VALID_SYMP()),
    Field('created', 'datetime', default=request.now, writable=False),
    Field('modified', 'datetime', default=request.now, update=request.now, writable=False),
    
    format='%(title)s'
)


#TODO ADD ON CREATE RUN EMAIL/UPDATE PAPER ROUTINE
db.define_table('paper_comment',
    Field('paper', db.paper, writable=False),
    Field('author', db.auth_user, default=auth.user, writable=False, represent=lambda x: db.auth_user._format % x),
    Field('status', 'string', requires=IS_IN_SET(PAPER_STATUS)),
    Field('created', 'datetime', default=request.now, writable=False),
    Field('comment', 'text')
    )
