# coding: utf8

class IS_VALID_SYMP(object):
    """
    This Validator class only gives options of symposiums that are
    currently accepting submissions (within registration period).
    
    It will also accept any symposium that is valid.
    """
    def __init__(self, error_message='This Symposium is not or no longer accepting registrations'):
        self.error_message = error_message
        self.multiple=False
        
    def __call__(self, value):
        """
        Checks value (symposium id) against the symposium database
        
        Returns the value, None if accepts and Value, Error String
        if it does not.
        """
        try:
            if db(db.symposium.id == value).select().first():
            # Check if a valid opbject, this will allow old reg to work but not add new ones    
            #if value.reg_end > request.now and value.reg_start < request.now:
                return (value, None)

            else:
                return (value, self.error_message)

        except:
            return (value, self.error_message)
            
    def options(self):
        """
        Returns a list of symposiums [(id, name), ...] or
        [(-1, T('No Symposiums Available At This Time')] if no
        symposiums are accepting new submissions
        """
        r = [(x.id, db.symposium._format % x)
            for x in db(db.symposium.reg_end > request.now).select(orderby=db.symposium.event_date)]
        return r or [(-1, T('No Symposiums Available At This Time'))]
        
    def formatter(self, value):
        """
        Maps ID to Symposium Name
        """
        v = db.symposium(value)
        if v:
            return db.symposium._format % v
        else:
            "NONE"
