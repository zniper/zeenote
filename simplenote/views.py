from django.template import Template, Context, RequestContext
from django.template.loader import get_template
from django.http import HttpResponse
from django.shortcuts import render_to_response,render
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.utils import simplejson
from django.core.mail import EmailMessage
import cgi
import base64

import logging
import threading
import datetime
import time
from operator import itemgetter, attrgetter

from simplenote.forms import NoteEditForm
from simplenote.models import BasicNote, UserImportKey, ShareNote ,FeedBack
from simplenote.utils import getTimeSt
from simplenote.extract import DiffBotExtracter,ExtractText

logger = logging.getLogger(__name__)

ACT_UPDATE_TITLE = '1'
ACT_UPDATE_CONTENT = '2'
ACT_GET_LIST = '3'
ACT_TRASH = '4'
ACT_CREATE = '5'
ACT_SHARE = '6'
ACT_SEARCH = '7'
ACT_DONT_SHARE = '8'
ACT_ADD_TAG = '9'
ACT_LOAD_LIST_BY_TAG = '10'
ACT_REMOVE_TAG = '11'
ACT_LOAD_TRASH = '12'
ACT_DELETE = '13'
ACT_RESTORE = '14'


NOTE_BOTTOM_LINE = """
@: %s
- - - - - - - - - - - - - - - - - 

"""

@login_required
def memberHomeView(request):
    """ Temporary not in-use
    """
    props = {'product_name':'',
             'categories'  :((1, 'One'), (2, 'Two')),
             'product_id'  :'',
             }
    props.update(csrf(request))
    return render_to_response('member/home.html',
                              props,
                              context_instance=RequestContext(request),
                              )

@login_required
def noteComposeView(request):
    context = {}
    if request.method == 'POST':
        form = NoteEditForm(request.POST)
        if form.is_valid():
            note = BasicNote()
            note.title = form.cleaned_data['title']
            note.content = form.cleaned_data['content']
            note.member = request.user
            note.last_modified = datetime.datetime.now()
            note.save()
    else:
        form = NoteEditForm()
        context['form'] = form
        context.update(csrf(request))
    return render_to_response('member/note_edit.html', 
                              context,
                              context_instance=RequestContext(request),
                              )

@login_required
def singleNoteView(request, note_id=None):
    try:
        context = {}
        if (note_id):
            note = BasicNote.objects.get(id=note_id)
            if note.member != request.user:
                raise
            context['note'] = note
        else:
            print "nothing"
        context.update(csrf(request))
        return render_to_response('member/note_view.html',
                                  context,
                                  RequestContext(request),
                                  )
    except:
        raise
        logger.error('Cannot view single note')

    # 500 should be here
    return None

def getTagsByUser(user):
    li = []
    for item in BasicNote.objects.filter(member=user,isTrash=False).order_by('-created'):
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
    print tags
    tags = sorted(tags,key=itemgetter(1),reverse=True)
    return tags[:8]

@login_required
def syncNoteHandler(request):
    """ This handles all sync actions of notes, getting list,...
    """

    action = request.POST.get('action', None)
    note_id = request.POST.get('note_id', None)
    
    # update the corresponding note
    res = {}
    try:
        if note_id:
            res['code'] = '1'
            note = BasicNote.objects.get(id=int(note_id))
            # prevent editing by shared person
            if not note.checkUpdatePermission(request.user):
                res['code'] = '-1' 
                raise
            # update title or content
            if action in (ACT_UPDATE_TITLE, ACT_UPDATE_CONTENT):
                if action == ACT_UPDATE_TITLE:
                    note.title = request.POST.get('note_title', '')
                # update note content
                elif action == ACT_UPDATE_CONTENT:
                    note.content = request.POST.get('note_content', '')
                note.last_modified = datetime.datetime.now()
                note.save()
            elif action == ACT_RESTORE:
                note.isTrash = False
                note.save(); 
	    elif action == ACT_DELETE:
                note.delete()          
            elif action == ACT_TRASH:
                # delete note
                note.isTrash = True
                note.save()
                allTags = getTagsByUser(request.user)
                res['tags'] = allTags
                
            elif action == ACT_SHARE:
                site = Site.objects.get_current()
                noteShare = BasicNote.objects.get(id=int(note_id))
		stringEncode = request.user.username+"/"+str(noteShare.created.strftime("%s"))+"/"+note_id
                stringEncode = stringEncode.encode("hex")
		noteShare.link = site.domain+"/member/share/"+stringEncode
		noteShare.isShare = True
		noteShare.save()
		res['link'] = noteShare.link
	    elif action == ACT_DONT_SHARE:
                noteShare = BasicNote.objects.get(id=int(note_id))
		noteShare.isShare = False
		noteShare.save()
		res['success'] = True
            elif action == ACT_REMOVE_TAG:
                note = BasicNote.objects.get(id=int(note_id))
                removeTag = request.POST.get('tag_remove', '')
                note.tags.remove(removeTag)
                listTag = note.tags.all()
                li=[]
                if (len(listTag)> 0):
                    for item in listTag:
                        li.append(item.name)
                allTags = getTagsByUser(request.user)
                res['all_tags'] = allTags
                res['listTag'] = li
            elif action == ACT_ADD_TAG:
                stringTag = request.POST.get('tags', '')
                listTag = stringTag.split(',')	
                note = BasicNote.objects.get(id=int(note_id))
                for item in listTag:
                    note.tags.add(item)
                tags = getTagsByUser(request.user)
                res['tag']= tags
        # just get the note list
        if action == ACT_LOAD_TRASH:
            notes = []
            for item in BasicNote.objects.filter(member=request.user,isTrash=True).order_by('-created'):
                time1 = item.created.strftime("%A %d %B %Y %H:%M")
                notes.append((item.id, 
                              item.title, 
                              time1,
                              ));
            res['notes'] = notes
        if action == ACT_GET_LIST:   
            # load owned and shared notes
            notes = []
            for item in BasicNote.objects.filter(member=request.user,isTrash=False).order_by('-created'):
                time1 = item.created.strftime("%A %d %B %Y %H:%M")
                
                notes.append((item.id, 
                              item.title, 
                              time1,
                              ));
            snotes = []
            allTags = getTagsByUser(request.user)
            res['tags'] = allTags
            for sn in ShareNote.objects.filter(user=request.user):
                note = sn.note
                snotes.append((note.id, note.title, getTimeSt(note.last_modified)))
            res['notes'] = notes
            res['snotes'] = snotes
        elif action == ACT_LOAD_LIST_BY_TAG:
            notes = []
            tagName = request.POST.get('tag_name','')
            li = BasicNote.objects.filter(tags__name__in=[tagName],isTrash=False)
            for item in li:
                if (item.member == request.user):
                    time1 = item.created.strftime("%A %d %B %Y %H:%M")
                
                    notes.append((item.id, 
                                  item.title, 
                                  time1,
                                 ));
            res['notes'] = notes
            print notes
	elif action == ACT_SEARCH:
	    notes = []
	    search_word = request.POST.get('search_word','').lower()
            for item in BasicNote.objects.filter(member=request.user,isTrash=False).order_by('-created'):
		if (item.title.lower().find(search_word) != -1 or item.content.lower().find(search_word) != -1):
                    search_index = item.content.lower().find(search_word);	
		    shortDes = searchShortDescription(item.content,search_index,search_word)	
		    notes.append((item.id, 
                              item.title, 
			      shortDes,
                              search_word,
                              3,
                              ));
	    
	    res['notes'] = notes
        
        
        elif action == ACT_CREATE:
            # create new note
            note = BasicNote()
            note.title = 'Untitled'
            note.original_url = ''
            note.content = ''
            note.member = request.user
            note.created = datetime.datetime.now()
            note.save()
            res['new_id'] = note.id
    except:
        raise
        logger.error('Error when performing synchronization')

    return HttpResponse(simplejson.dumps(res),
                        mimetype='application/json')

def searchShortDescription(search_content,search_index,search_word):
    index = 0 
    li = []
    shortDes = ""
    while index < len( search_content ):
	index = search_content.find( '.', index )
	li.append(index)
	if index > search_index:
	    break
	if index == -1:
            break
        index += 1
    if len(li) == 1 or len(li) == 0:
        if search_index != 0 :
	        shortDes = "..." + search_content[search_index:(search_index+100)]
        else :
            shortDes = search_content[search_index:(search_index+100)]
        if (search_index + 100) < len(search_content) :
            shortDes += "..." 
            
    else:
        start = li[len(li)-2] + 1
        end = li[len(li)-1]
        shortDes = "..." + search_content[start:end]
        if end < len(search_content):
            shortDes += "..."
    return shortDes


def loadNote(request, note_id):
    """ Return the note content to the page 
    """
    res = {'code':'0'}
    # update the corresponding note
    try:
        note = BasicNote.objects.get(id=int(note_id))
        # check if shared note
        if note.member != request.user:
            sn = ShareNote.objects.filter(note=note, user=request.user)
            if len(sn) == 0:
                raise
            res['shared'] = 1
        listTag = note.tags.all()
        li=[]
        if (len(listTag)> 0):
            for item in listTag:
                li.append(item.name) 
        res['content'] = note.content
        res['title'] = note.title
        res['code'] = '1'
	res['isShare'] = note.isShare
	res['linkShare'] = note.link
        res['listTag'] = li
    except:
        logger.error('Error when loading note content (id=%s)' % note_id)

    return HttpResponse(simplejson.dumps(res),
                        mimetype='application/json')


@csrf_exempt
def remoteAddHandler(request, key):
    """ This one handles the request for adding current web page 
        to new or a specified note
    """
    message = ''
    try:
        source = request.POST.get('source', '')
        content = request.POST.get('selection', '')
        # content will be whole page text if empty
        if not content:
            content = ExtractText(source)
        nid = request.POST.get('nid', '')
        print nid
        try: nid = int(nid)
        except: nid = ''        
        if content != '':
            # appending case
            if nid:
                note = BasicNote.objects.get(id=nid)
                user_id = int(request.POST.get('user_id', ''))
                if note.checkUpdatePermissionById(user_id):
                    content += NOTE_BOTTOM_LINE % source
                    note.content = content + note.content
                else:
                    raise
            # creating new case
            else:
                key_obj = UserImportKey.objects.get(import_key=key)
                user = key_obj.user
                note = BasicNote()
                note.title = request.POST.get('title', 'untitled')
                note.original_url = source
                note.content = content
                note.member = user
            note.created = datetime.datetime.now()
            note.save()
            message = 'Note saved successfully'
    except:
        # user not existing, error message is needed here
        message = 'Oops, something wrong happened'
    resObject = HttpResponse(message)
    resObject['Access-Control-Allow-Origin']  = '*'
    return resObject

# Return the the remote javascript with user key included
def getRemoteScript(request, key):
    # if not exsiting, 500 appears
    site = Site.objects.get_current()
    key_object = UserImportKey.objects.get(import_key=key)
    props = {'user_id':request.user.id,
             'import_key': key,
             'note_id': request.GET.get('nid', ''),
             'site_domain': site.domain,
             }
    js_content = get_template('member/remote0.js').render(Context(props))
    return HttpResponse(js_content, mimetype='text/plain')
#trungnq : Get feedback and send feedback email to admin
#abc
class myThread (threading.Thread):
    def __init__(self, threadID, name, counter, email, content):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.email = email
        self.content = content
    def run(self):
        sendEmail(self.name, self.counter, 1, self.email, self.content)
        print "Exit"

def sendEmail(name, delay, counter, email, content):
    sendEmail_flag = 1
    while counter:
        if counter==0:
            thread.exit()
        emailSubject = "Zeenote's Feedback"
	emailContent = "A new Zeenote's Feedback\n\n User     : %s\n Email    :%s\n Content  :%s" % (name,email,content)
	email = EmailMessage(emailSubject, emailContent, to=['trungnq111@gmail.com'])
	email.send()
        print "hehe"
        counter -= 1


def feedback(request):
    success = False
    if request.method == "POST":
	email = request.POST.get('email','')
	name  = request.POST.get('name','')
	content  = request.POST.get('content','')
        isUser = request.POST.get('isUser','')
        if isUser == 1:
	    feedback = FeedBack()
	    feedback.user = request.user
	    feedback.content = content
	    feedback.staus = False
	    feedback.save()
        success = True
        #sendMailThread = myThread(1,name, email, content)
        #sendMailThread.start()
        thread1 = myThread(1, name, 1,email,content)
        thread1.start()
    return HttpResponse(success)


def viewNoteShare(request,string):
    stringDecode = string.decode("hex")
    noteId = stringDecode.split("/")[2]
    note = BasicNote.objects.get(id=int(noteId))
    res = {}
    if note.isShare == True:
	    res['title'] = note.title
	    res['content'] = note.content
    else:
	    res['content'] = "Not Share"
    return render(request, 'member/view_note_share.html', res)

#---------------------------------------------
def about(request):
    return render_to_response('about.html', context_instance=RequestContext(request),)
def home(request):
    return render_to_response('index.html', context_instance=RequestContext(request),)
def guide(request):
    return render_to_response('guide.html', context_instance=RequestContext(request),)
