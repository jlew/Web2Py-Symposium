# coding: utf8

def _setup_api_request( db_type ):
    """
    Preloads response_flags with request information, setus up page limits,
    enforces extenstion
    """
    # Force only JSON, XML, or LOAD requests
    if request.extension not in ['xml','json', 'load']:
        raise HTTP(501, "API Only supports xml, json, and load (html debugging representation)")

    #Populate Response/Request Flags
    response_flags = {
        'request': {
            'time': str(request.now),
            'vars': request.vars,
            'args': request.args,
            'url': request.url,
            'user': {
                    "Name":db.auth_user._format % auth.user,
                    "ID":auth.user.id
                } if auth.user else None
            },
        'result_info': {}
        }
    query_filters = {}
    
    # Set page and limit
    if request.vars.perpage != "all":
        page = int(request.vars.page) if (request.vars.page or "").isdigit() else 1
        perpage = int(request.vars.perpage) if (request.vars.perpage or "").isdigit() else 25
        response_flags['result_info']['page'] = page
        response_flags['result_info']['per_page'] = perpage
        query_filters['limitby'] = ((page-1)*perpage,page*perpage)
        
    # Set order
    if request.vars.sort:
        if db_type.has_key( request.vars.sort ):
            if request.vars.sortdir and request.vars.sortdir == "desc":
                query_filters['orderby'] = ~db_type[request.vars.sort]
            else:
                query_filters['orderby'] = db_type[request.vars.sort]
    
    # Automatically Filter fields
    response_fields = []
    if request.vars.fields:
        field_list = request.vars.fields.split("|")
        
        for field in field_list:
            if db_type.has_key(field):
                # Make sure non-admins can't ask for protected values
                if field in API_SAFE[db_type._tablename] or auth.has_membership("Symposium Admin"):
                    response_fields.append( db_type[field] )
                else:
                    response_flags['result_info']['errors'] = response_flags['result_info'].get('errors', []) + ["Protected Field: %s" % field]
            else:
                response_flags['result_info']['errors'] = response_flags['result_info'].get('errors', []) + ["Unknown Field: %s" % field]
        
    # If no fields requested and not admin, use API_SAFE fields
    # Otherwise leave response_fields empty which will publish all fields
    if len( response_fields ) == 0 and not auth.has_membership("Symposium Admin"):
        for field in API_SAFE[db_type._tablename]:
            response_fields.append( db_type[field] )
            
    response_flags['result_info']['fields'] = [x.name for x in response_fields]

    return response_flags, query_filters, response_fields

def _do_query(query, filters, response_flags, response_fields):
    """
    Builds and executes the final query.  Returns record counts, pages,
    and the results of the query.
    """
    result = db(query).select(*response_fields, **filters)
    response_flags['result_info']['records'] = db(query).count()
    response_flags['result_info']['total_pages'] = response_flags['result_info']['records'] / response_flags['result_info']['per_page']
    
    # TODO: REMOVE ME
    response_flags['result_info']['sql'] = {
        'query': str(query),
        'filters': str(filters),
    }
        
        
    response_flags['result'] = result.as_list()
    return dict(api=response_flags)


    return response_fields

def index(): return dict(message="hello from api.py")

def symposiums():
    response_flags, query_filters, response_fields = _setup_api_request(db.symposium)
    query = (db.symposium.id > 0)
     
    # Run Request
    return _do_query(query, query_filters, response_flags, response_fields)

def papers():
    response_flags, query_filters, response_fields = _setup_api_request(db.paper)
    query = (db.paper.id > 0)
    
    # Filter Out non-visble if non-admin
    if auth.has_membership("Symposium Admin") and request.vars.show_private:
        response_flags['result_info']['filter_public'] = False
    else:
        response_flags['result_info']['filter_public'] = True
        status_filter = False
        for status_option in [PAPER_STATUS[x] for x in VISIBLE_STATUS]:
            if status_filter:
                status_filter = status_filter | (db.paper.status == status_option)
            else:
                status_filter = (db.paper.status == status_option)
        query = query & status_filter
    
    # Run Request
    return _do_query(query, query_filters, response_flags, response_fields)
    
def people():
    response_flags, query_filters, response_fields = _setup_api_request(db.auth_user)
    query = (db.auth_user.id > 0)
     
    # Run Request
    return _do_query(query, query_filters, response_flags, response_fields)
