# Utils.py heavily inspired by utils.py seen in guess a number project.

from google.appengine.ext import ndb
import endpoints

def get_by_urlsafe(urlsafe, model):
    """ Retrieves ndb.Model entity that the urlsafe value points to.
    If it doens't work, it returns an exception.
    """

    try:
        key = ndb.Key(urlsafe=urlsafe)
    except TypeError:
        raise endpoints.BadRequestException('Invalid Key')
    except Exception, e:
        if e.__class__.__name__ == 'ProtocolBufferDecodeError':
            raise endpoints.BadRequestException('Invalid Key')
        else:
            raise

    entity = key.get()
    if not entity:
        return None
    if not isinstance(entity, model):
        raise ValueError('Incorrect Kind')
    return entity
    