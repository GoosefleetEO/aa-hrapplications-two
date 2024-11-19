from django.contrib import admin

from .models import Application, ApplicationChoice, ApplicationComment, ApplicationForm, ApplicationQuestion, \
    ApplicationResponse, ApplicationAcceptedFilter


class ChoiceInline(admin.TabularInline):
    model = ApplicationChoice
    extra = 0
    verbose_name_plural = 'Choices (optional)'
    verbose_name= 'Choice'

@admin.register(ApplicationQuestion)
class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
            (None, {'fields': ['title', 'help_text', 'multi_select']}),
            ]
    inlines = [ChoiceInline]

admin.site.register(Application)
admin.site.register(ApplicationComment)
admin.site.register(ApplicationForm)
admin.site.register(ApplicationResponse)

class ApplicationAcceptedAdmin(admin.ModelAdmin):
    raw_id_fields = ['filter_corp']

admin.site.register(ApplicationAcceptedFilter, ApplicationAcceptedAdmin)