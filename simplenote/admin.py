from django.contrib import admin
from models import BasicNote, UserImportKey, ShareNote , FeedBack
from django.core.mail import send_mail


#trungnq
class FeedBackAdmin(admin.ModelAdmin):
    readonly_fields = ('content','user')
    fields = ['user', 'content','rates']
	
    list_display = ('user', 'content','status', 'send_email_html')

    def send_email_html(self, obj):
        # example using a javascript function send_email()
        return '<a href="mailto:%s">Reply</a>' % obj.user.email
    send_email_html.short_description = 'Send Email'
    send_email_html.allow_tags = True

#----------------------------------------

admin.site.register(BasicNote)
admin.site.register(UserImportKey)
admin.site.register(ShareNote)
admin.site.register(FeedBack,FeedBackAdmin)
