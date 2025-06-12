from collections import defaultdict

from django.contrib.auth.models import User
from django.db import models
from django.apps import apps
from sortedm2m.fields import SortedManyToManyField

from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo

from .managers import ApplicationManager

class ApplicationQuestion(models.Model):
    title = models.CharField(max_length=254, verbose_name='Question')
    help_text = models.CharField(max_length=254, blank=True, null=True)
    multi_select = models.BooleanField(default=False)

    def __str__(self):
        return "Question: " + self.title


class ApplicationChoice(models.Model):
    question = models.ForeignKey(ApplicationQuestion,on_delete=models.CASCADE,related_name="choices")
    choice_text = models.CharField(max_length=200, verbose_name='Choice')

    def __str__(self):
        return self.choice_text


class ApplicationForm(models.Model):
    questions = SortedManyToManyField(ApplicationQuestion)
    corp = models.OneToOneField(EveCorporationInfo, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.corp)


class Application(models.Model):
    form = models.ForeignKey(ApplicationForm, on_delete=models.CASCADE, related_name='applications')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    approved = models.BooleanField(blank=True, null=True, default=None)
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    reviewer_character = models.ForeignKey(EveCharacter, on_delete=models.SET_NULL, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = ApplicationManager()

    def __str__(self):
        return str(self.user) + " Application To " + str(self.form)

    class Meta:
        permissions = (
            ('approve_application', 'Can approve applications'),
            ('access_application', 'Can access HR application'),)
        unique_together = ('form', 'user')

    @property
    def main_character(self):
        return self.user.profile.main_character

    @property
    def characters(self):
        return [o.character for o in self.user.character_ownerships.all()]

    @property
    def discord_users(self):
        if apps.is_installed('aadiscordmultiverse'):
            return self.user.multidiscorduser_set.all()
        return None

    @property
    def reviewer_str(self):
        if self.reviewer_character:
            return str(self.reviewer_character)
        elif self.reviewer:
            return "User " + str(self.reviewer)
        else:
            return None


class ApplicationResponse(models.Model):
    question = models.ForeignKey(ApplicationQuestion, on_delete=models.CASCADE)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='responses')
    answer = models.TextField()

    def __str__(self):
        return str(self.application) + " Answer To " + str(self.question)

    class Meta:
        unique_together = ('question', 'application')


class ApplicationComment(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user) + " comment on " + str(self.application)

class FilterBase(models.Model):

    name = models.CharField(max_length=500)
    description = models.CharField(max_length=500)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.name}: {self.description}"

    def process_filter(self, user: User):
        raise NotImplementedError("Please Create a filter!")

    def audit_filter(self, users):
        raise NotImplementedError("Please Create an audit function!")

class ApplicationAcceptedFilter(FilterBase):
    class Meta:
        verbose_name = "Smart Filter: Accepted Application for Corp"
        verbose_name_plural = verbose_name

    filter_corp = models.ForeignKey(EveCorporationInfo, on_delete=models.CASCADE)

    def __str__(self):
        return f"Application accepted for {self.filter_corp.corporation_name}"

    def process_filter(self, user: User):

        if not user.applications.exists():
            return False

        applications = user.applications.filter(form__corp=self.filter_corp, approved=True).count()
        if applications:
            return True

        return False

    def audit_filter(self, users):
        apps = Application.objects.filter(user__in=users, form__corp=self.filter_corp).values('user__id','approved','reviewer')

        if not apps.count():
            return defaultdict(lambda: {"message": "No Application Found", "check": False})

        output = defaultdict(lambda: {"message": "No Application Found", "check": False})
        for a in apps:
            result = False
            if a['approved']:
                message = "Accepted"
                result = True
            elif a['approved'] is None and a['reviewer'] is not None:
                message = "In Review"
            elif a['approved'] is None:
                message = "Pending"
            else:
                message = "Rejected"
            output[a['user__id']] = {"message": f"Application {message}", "check": result}

        return output

class ApplicationRejectedFilter(FilterBase):
    class Meta:
        verbose_name = "Smart Filter: Rejected Application for Corp"
        verbose_name_plural = verbose_name

    filter_corp = models.ForeignKey(EveCorporationInfo, on_delete=models.CASCADE)

    def __str__(self):
        return f"Application rejected for {self.filter_corp.corporation_name}"

    def process_filter(self, user: User):

        if not user.applications.exists():
            return False

        applications = user.applications.filter(form__corp=self.filter_corp, approved=False).count()
        if applications:
            return True

        return False

    def audit_filter(self, users):
        apps = Application.objects.filter(user__in=users, form__corp=self.filter_corp).values('user__id','approved','reviewer')

        if not apps.count():
            return defaultdict(lambda: {"message": "No Application Found", "check": False})

        output = defaultdict(lambda: {"message": "No Application Found", "check": False})
        for a in apps:
            result = False
            if a['approved']:
                message = "Accepted"
            elif a['approved'] is None and a['reviewer'] is not None:
                message = "In Review"
            elif a['approved'] is None:
                message = "Pending"
            else:
                message = "Rejected"
                result = True                
            output[a['user__id']] = {"message": f"Application {message}", "check": result}

        return output
        
class ApplicationPendingReviewFilter(FilterBase):
    class Meta:
        verbose_name = "Smart Filter: Application for Corp Pending Review"
        verbose_name_plural = verbose_name

    filter_corp = models.ForeignKey(EveCorporationInfo, on_delete=models.CASCADE)

    def __str__(self):
        return f"Application pending review for {self.filter_corp.corporation_name}"

    def process_filter(self, user: User):

        if not user.applications.exists():
            return False

        applications = user.applications.filter(form__corp=self.filter_corp, approved__isnull=True, reviewer__isnull=True).count()
        if applications:
            return True

        return False

    def audit_filter(self, users):
        apps = Application.objects.filter(user__in=users, form__corp=self.filter_corp).values('user__id','approved','reviewer')

        if not apps.count():
            return defaultdict(lambda: {"message": "No Application Found", "check": False})

        output = defaultdict(lambda: {"message": "No Application Found", "check": False})
        for a in apps:
            result = False
            if a['approved']:
                message = "Accepted"
            elif a['approved'] is None and a['reviewer'] is not None:
                message = "In Review"
            elif a['approved'] is None:
                message = "Pending"
                result = True                
            else:
                message = "Rejected"                
            output[a['user__id']] = {"message": f"Application {message}", "check": result}

        return output
        
class ApplicationInReviewFilter(FilterBase):
    class Meta:
        verbose_name = "Smart Filter: Application for Corp In Review"
        verbose_name_plural = verbose_name

    filter_corp = models.ForeignKey(EveCorporationInfo, on_delete=models.CASCADE)

    def __str__(self):
        return f"Application in review for {self.filter_corp.corporation_name}"

    def process_filter(self, user: User):

        if not user.applications.exists():
            return False

        applications = user.applications.filter(form__corp=self.filter_corp, approved__isnull=True, reviewer__isnull=False).count()
        if applications:
            return True

        return False

    def audit_filter(self, users):
        apps = Application.objects.filter(user__in=users, form__corp=self.filter_corp).values('user__id','approved','reviewer')

        if not apps.count():
            return defaultdict(lambda: {"message": "No Application Found", "check": False})

        output = defaultdict(lambda: {"message": "No Application Found", "check": False})
        for a in apps:
            result = False
            if a['approved']:
                message = "Accepted"
            elif a['approved'] is None and a['reviewer'] is not None:
                message = "In Review"
                result = True                
            elif a['approved'] is None:
                message = "Pending"
            else:
                message = "Rejected"                
            output[a['user__id']] = {"message": f"Application {message}", "check": result}

        return output
        
class ApplicationExistsFilter(FilterBase):
    class Meta:
        verbose_name = "Smart Filter: Application for Corp Exists"
        verbose_name_plural = verbose_name

    filter_corp = models.ForeignKey(EveCorporationInfo, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Application exists for {self.filter_corp.corporation_name}"

    def process_filter(self, user: User):

        if not user.applications.exists():
            return False

        applications = user.applications.filter(form__corp=self.filter_corp).count()
        if applications:
            return True

        return False

    def audit_filter(self, users):
        apps = Application.objects.filter(user__in=users, form__corp=self.filter_corp).values('user__id','approved','reviewer')

        if not apps.count():
            return defaultdict(lambda: {"message": "No Application Found", "check": False})

        output = defaultdict(lambda: {"message": "No Application Found", "check": False})
        for a in apps:
            result = True
            if a['approved']:
                message = "Accepted"
            elif a['approved'] is None and a['reviewer'] is not None:
                message = "In Review"      
            elif a['approved'] is None:
                message = "Pending"
            else:
                message = "Rejected"                
            output[a['user__id']] = {"message": f"Application {message}", "check": result}

        return output