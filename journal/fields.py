from django.forms.models import ModelChoiceField


class MyModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.date_of_visit.strftime('%Y-%m-%d')