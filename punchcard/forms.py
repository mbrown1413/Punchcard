import re
from datetime import date

from django import forms

from punchcard.models import Category, Entry
from punchcard import bootstrapforms

category_name_re = re.compile(r'^[A-Za-z0-9_\- ]+$')


class SortedSelectWidget(forms.widgets.Select):

    def render(self, *args, **kwargs):
        self.choices = sorted(self.choices, key=lambda x: x[1])
        return super(SortedSelectWidget, self).render(*args, **kwargs)


class EntryForm(forms.ModelForm):

    class Meta:
        model = Entry
        fields = '__all__'
        widgets = {
            'category': SortedSelectWidget(),
        }

    def __init__(self, *args, **kwargs):
        super(EntryForm, self).__init__(*args, **kwargs)

        # Set date to today if form not bound
        if not self.is_bound:
            self.fields['date'].initial = date.today()


class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = '__all__'
        widgets = {
            'parent': SortedSelectWidget(),
        }

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)

        # If instance provided, only allow parent choices that wouldn't create
        # a loop
        instance = kwargs['instance']
        if instance:
            valid_parents = instance.get_valid_parents()
            choices = map(lambda x: (x.id, x.full_path), valid_parents)
            self.fields['parent'].choices = choices

    def clean_name(self):
        value = self.cleaned_data['name']
        if not category_name_re.match(value):
            raise forms.ValidationError("Name can only contain letters, numbers, spaces, underscores and hyphens", code="invalid")
        return value


class CategoryAddForm(CategoryForm):

    class Meta:
        model = Category
        exclude = ['active']
        widgets = {
            'parent': SortedSelectWidget(),
        }
