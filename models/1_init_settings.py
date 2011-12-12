# coding: utf8

# Using ConfigParser to read config in ini
# Allows us to prevent sensitive data in our repo
from os.path import join
from ConfigParser import SafeConfigParser

config = SafeConfigParser()
config.read(join(request.folder, 'config.ini'))

db = DAL(config.get('db','connection'))

#########################################################################
## Setup:
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - crud
#########################################################################

from gluon.tools import Mail, Auth, Crud, Service, PluginManager, prettydate
mail = Mail()                                  # mailer
auth = Auth(db)                                # authentication/authorization
crud = Crud(db)                                # for CRUD helpers using auth
service = Service()                            # for json, xml, jsonrpc, xmlrpc, amfrpc
plugins = PluginManager()                      # for configuring plugins

mail.settings.server = config.get('mail','server')  # your SMTP server
mail.settings.sender = config.get('mail','sender')  # your email
mail.settings.tls = config.get('mail','tls')
mail.settings.login = config.get('mail','login')    # your credentials or None

def Hidden(*a,**b):
    b['writable']=b['readable']=False
    return Field(*a,**b)
    
fields=[
    Field('first_name', length=512,default='',comment='*'),
    Field('last_name', length=512,default='',comment='*'),
    Field('affiliation', length=512, label='Current Affiliation/Title',
           default="Rochester Institute of Technology, Student", required=True, comment=T("This is the affiliation that will be shown on your profile.  You may override this for specific papers.")),
    Field('email', length=512,default='',comment='*',
          requires=(IS_EMAIL(),IS_NOT_IN_DB(db,'auth_user.email'))),
    Field('password', 'password', readable=False, label='Password',
          requires=[CRYPT(auth.settings.hmac_key)]),
    Field('web_page',requires=IS_EMPTY_OR(IS_URL())),
    Field('mobile_number',default=''),    
    Field('short_profile','text',default=''),
    Field('profile_picture','upload', autodelete=True, requires=IS_EMPTY_OR(IS_IMAGE())),
    Hidden('registered_by','integer',default=0), #nobody
    Hidden('search_name',compute=lambda r: "%s %s (%s)" %( r['first_name'], r['last_name'], r['affiliation'])),
    Hidden('registration_id', length=512,default=''),
    Hidden('registration_key', length=512,default=''),
    Hidden('reset_password_key', length=512,default='',
          label=auth.messages.label_reset_password_key),
    ]

db.define_table('auth_user',
                format='%(first_name)s %(last_name)s (%(affiliation)s)',
                *fields
                )

auth.settings.create_user_groups = False
auth.settings.hmac_key = config.get('auth','hmac_key')   # before define_tables()
auth.define_tables()                           # creates all needed tables
auth.settings.mailer = mail                    # for user email verification
auth.settings.registration_requires_verification = config.getboolean('auth','verification')
auth.settings.registration_requires_approval =  config.getboolean('auth','approval')
auth.messages.verify_email = 'Click on the link http://'+request.env.http_host+URL('default','user',args=['verify_email'])+'/%(key)s to verify your email'
auth.settings.reset_password_requires_verification = True
auth.messages.reset_password = 'Click on the link http://'+request.env.http_host+URL('default','user',args=['reset_password'])+'/%(key)s to reset your password'
auth.messages.email_sent = T("Verificaion Email Sent, please verify your email before you login")

crud.settings.auth = None        # =auth to enforce authorization on crud
