from .models import ApplicationForm, ApplicationRejectedFilter, ApplicationAcceptedFilter, ApplicationInReviewFilter, ApplicationPendingReviewFilter, ApplicationExistsFilter

from django.db.models.signals import post_save, pre_delete
from django.dispatch import Signal, receiver

@receiver(post_save, sender=ApplicationForm)
def make_filterstrigger(sender, instance, **kwargs):
    ApplicationRejectedFilter.objects.update_or_create(filter_corp=instance.corp,name="App Rejected",description=instance.corp.corporation_name)
    ApplicationAcceptedFilter.objects.update_or_create(filter_corp=instance.corp,name="App Accepted",description=instance.corp.corporation_name)
    ApplicationInReviewFilter.objects.update_or_create(filter_corp=instance.corp,name="App In Review",description=instance.corp.corporation_name)
    ApplicationPendingReviewFilter.objects.update_or_create(filter_corp=instance.corp,name="App Pending",description=instance.corp.corporation_name)
    ApplicationExistsFilter.objects.update_or_create(filter_corp=instance.corp,name="App Exists",description=instance.corp.corporation_name)

@receiver(pre_delete, sender=ApplicationForm)
def del_filterstrigger(sender, instance, **kwargs):
    ApplicationRejectedFilter.objects.filter(filter_corp=instance.corp).delete()
    ApplicationAcceptedFilter.objects.filter(filter_corp=instance.corp).delete()
    ApplicationInReviewFilter.objects.filter(filter_corp=instance.corp).delete()
    ApplicationPendingReviewFilter.objects.filter(filter_corp=instance.corp).delete()
    ApplicationExistsFilter.objects.filter(filter_corp=instance.corp).delete()
