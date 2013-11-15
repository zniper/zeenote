from django.dispatch import receiver
from registration.signals import user_registered
from simplenote.models import UserImportKey

import datetime
import hashlib
import random
import logging

logger = logging.getLogger(__name__)

@receiver(user_registered)
def initUserImportKey(sender, **kwargs):
    # generate and ensure no duplication
    dup = True
    now = datetime.datetime.now().strftime('%y%m%d%H%M%S')
    new_key = ''
    while dup:
        new_key = hashlib.md5(now).hexdigest()
        try:
            user_key = UserImportKey.objects.get(import_key=new_key)
        except:
            break
        # having duplication, rehash
        now += str(random.randint(1, 10))
        continue

    # save the record
    user_key = UserImportKey()
    user_key.user = kwargs['user']
    user_key.import_key = new_key
    user_key.save()


# Query and return single import key of an user
def getUserKey(user):
    user_key = None
    if user:
        try:
            key_object = UserImportKey.objects.get(user=user)
            user_key = key_object.import_key
        except:
            logger.error('Error when getting user import key')
    return user_key

            
def getTimeSt(moment, kind='comparable'):
    """ Convert datetime value to string
    """
    timeSt = '-'
    try:
        if kind == 'comparable':
            timeSt = moment.strftime('%y%m%d%H%M%S')
    except:
        pass
    return timeSt
