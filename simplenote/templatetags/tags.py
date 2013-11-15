from django import template
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

import logging 
from datetime import date,time

from simplenote import models
from simplenote import settings
from operator import itemgetter, attrgetter


logger = logging.getLogger(__name__)
register = template.Library()


@register.inclusion_tag('member/note_list.html', takes_context=True)
def list_my_notes(context):
    notes = ()
    cur_note = None
    he = ""
    try:
        notes = models.BasicNote.objects.filter(member=context['user'],isTrash=False).order_by('-created')
        cur_note = context.get('note', None)
        for item in notes:
            time1 = item.created.strftime("%A %d %B %Y %H:%M")
            item.created  = time1
    except:
        print "error"
    return {'all_notes':notes,
            'note':cur_note,
           }


@register.inclusion_tag('member/share_list.html', takes_context=True)
def list_shared_notes(context):
    notes = ()
    cur_note = None
    try:
        shares = models.ShareNote.objects.filter(user=context['user'])
        notes = [s.note for s in shares]
    except:
        logger.error('Error when getting shared notes')
         
    return {'all_notes':notes}


@register.inclusion_tag('member/tag_list.html', takes_context=True)
def list_tags(context):
    cur_note = None
    try:
        li = []
        for item in models.BasicNote.objects.filter(member=context['user'],isTrash=False).order_by('-created'):
            for index in range(len(item.tags.all())):
                li.append(item.tags.all()[index].name)
        liTag = []
        tags = []
        for item in li:
            if (item in liTag) == False:
                liTag.append(item)
                content = []
                content.append(item)
                content.append(li.count(item)) 
                tags.append(content)   
        tags = sorted(tags,key=itemgetter(1),reverse=True)

    except:
        logger.error('Error when getting list tags')
         
    return {'all_tags':tags[:8]}



@register.simple_tag(takes_context=True)
def bookmark_new_note(context):
    """ Return the javascript which is used for saving to separate note
    """
    user = context['user']
    key_object = models.UserImportKey.objects.get(user=user)
    user_key = key_object.import_key
    site = Site.objects.get_current()

    bookmark  = "javascript:function%20iprl5(){var%20d=document,z=d.createElement('script'),b=d.body,"
    bookmark += "l=d.location;try{if(!b)throw(0);z.setAttribute('src','http://" + site.domain
    bookmark += "/member/rjs/" + user_key + "');b.appendChild(z);}catch(e){alert('Please%20wait%20until"
    bookmark += "%20the%20page%20has%20loaded.');}}%20iprl5();void(0)"
    return bookmark


@register.simple_tag(takes_context=True)
def bookmark_append_note(context, note_id):
    """ Return the javascript which is used for saving to separate note
    """
    user = context['user']
    key_object = models.UserImportKey.objects.get(user=user)
    user_key = key_object.import_key
    site = Site.objects.get_current()
    bookmark  = "javascript:function%20iprl5(){var%20d=document,z=d.createElement('script'),b=d.body,"
    bookmark += "l=d.location;try{if(!b)throw(0);z.setAttribute('src','http://" + site.domain
    bookmark += "/member/rjs/" + user_key + "?nid=" + note_id + "');b.appendChild(z);}"
    bookmark += "catch(e){alert('Please%20wait%20until%20the%20page%20has%20loaded.');}}%20iprl5();void(0)"
    return bookmark

