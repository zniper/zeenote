from django.db import models
from django.contrib.auth.models import User
from taggit.managers import TaggableManager

import pdb

RATING_CHOICES = (
    ("1", 1),
    ("2", 2),
    ("3", 3),
    ("4", 4),
    ("5", 5),
)


class ItemBase(models.Model):
    member = models.ForeignKey(User)
    original_url = models.CharField(max_length=255)
    original_source = models.CharField(max_length=255)
    last_modified = models.DateTimeField(null=True)
    title = models.CharField(max_length=255)
    created= models.DateTimeField(null=False)
    tag = models.CharField(max_length=255) 
    link = models.CharField(max_length=255)
    isShare = models.BooleanField()
    isTrash = models.BooleanField()
    
    tags = TaggableManager()
    

class BasicNote(ItemBase):
    content = models.TextField()

    def __unicode__(self):
        return 'BasicNote: '+self.title

    def checkSharing(self, user):
        """ Check if user is shared to use specified note or not
        """
        if user:
            snote = ShareNote.objects.filter(user=user, note=self)
            return (len(snote) > 0)
        return False

    def checkSharingById(self, uid):
        """ Check sharing by user and note id 
        """
        try:
            user = User.objects.get(id=uid)
            return self.checkSharing(user, self)
        except:
            pass
        return False
    
    def checkUpdatePermissionById(self, uid):
        """ Check if specific user having permission to update
        """
        print uid
        return (uid == self.member.id or self.checkSharingById(uid))
            
    def checkUpdatePermission(self, user):
        """ Check if specific user having permission to update
        """
        return (user == self.member or self.checkSharing(user))


class UserImportKey(models.Model):
    user = models.ForeignKey(User)
    import_key = models.CharField(max_length=48)
    def __unicode__(self):
        return 'UserImportKey: '+self.user.username
    
class FeedBackManager(models.Manager):
    def read_message(self, FeedBack_id):
        # This won't fail quietly it'll raise an ObjectDoesNotExist exception
        message = super(FeedBackManager, self).get(pk=FeedBack_id)
        message.status = True
        message.save()
        return message

#trungnq
class FeedBack(models.Model):
    user = models.ForeignKey(User)
    content = models.CharField(max_length=300) 
    rates = models.CharField(max_length=5,choices=RATING_CHOICES)
    status = models.BooleanField()
    
    def save(self, *args, **kwargs):
        self.status = True
        super(FeedBack, self).save(*args, **kwargs) # Call the "real" save() method.

    def __unicode__(self):
        return 'FeedBack: %s' % (self.user.username)
#------------------------------------------------------	
	

class ShareNote(models.Model):
    user = models.ForeignKey(User)
    note = models.ForeignKey(BasicNote)
    accepted = models.BooleanField()

    def __unicode__(self):
        return 'SharedNote: %s (+%s) + %s' % (self.note.title, self.user.username,self.accepted)

