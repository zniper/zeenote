from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from simplenote.views import memberHomeView

urlpatterns = patterns('',
    url(r'^$', 'simplenote.views.singleNoteView' , name='member_home'),
    url(r'^note/?$', 'simplenote.views.singleNoteView' , name='member_home'),
    url(r'^note/(\d+)$', 'simplenote.views.singleNoteView' , name='view_note'),
    url(r'^sync/?$', 'simplenote.views.syncNoteHandler' , name='sync_note'),
    url(r'^load/(\d+)?$', 'simplenote.views.loadNote' , name='load_note'),
    url(r'^radd/(\w+)/?$', 'simplenote.views.remoteAddHandler' , name='remote_add'),
    url(r'^rjs/(\w+)/?$', 'simplenote.views.getRemoteScript', name='remote_js'),
    url(r'^feedback/?$', 'simplenote.views.feedback' , name='feedback'),
    url(r'^share/(\w+)?$', 'simplenote.views.viewNoteShare' , name='view_note_share'),
)
