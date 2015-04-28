from django.contrib import admin

from contact.models import Contact, Newsletter, Topic, QA


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    pass

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    pass

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    pass

@admin.register(QA)
class QAAdmin(admin.ModelAdmin):
    pass