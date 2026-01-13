from .mambuconfig import apiurl

def getmambuurl(url=apiurl, *args, **kwargs):
    """Basic Mambu URL function. Builds the Mambu basic request string.

    Receives a user, password and url arguments to connect to Mambu.
    Defaults to what mambuconfig has, but you may override it by sending
    'user', 'pwd' and 'url' parameters at the Mambu object instantiation
    (for instance: MambuLoan(user=myuser, pwd=mypwd, url=myurl,
    entid='12345', ...)

    .. todo:: status API V2: compatible
    """
    mambuurl = "https://" + url + "/api/"
    return mambuurl
