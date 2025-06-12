from django.contrib import admin

from .models import Application, ApplicationChoice, ApplicationComment, ApplicationForm, ApplicationQuestion, \
    ApplicationResponse, ApplicationAcceptedFilter, ApplicationRejectedFilter, ApplicationInReviewFilter, ApplicationPendingReviewFilter, ApplicationExistsFilter


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

class ApplicationFiltersAdmin(admin.ModelAdmin):
    readonly_fields = ["filter_corp"]

admin.site.register(ApplicationAcceptedFilter, ApplicationFiltersAdmin)
admin.site.register(ApplicationRejectedFilter, ApplicationFiltersAdmin)
admin.site.register(ApplicationPendingReviewFilter, ApplicationFiltersAdmin)
admin.site.register(ApplicationInReviewFilter, ApplicationFiltersAdmin)
admin.site.register(ApplicationExistsFilter, ApplicationFiltersAdmin)