from datetime import date
from itertools import imap
from collections import defaultdict

from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.base import TemplateView

from punchcard import models, forms, dateutils


#################### Entries ####################

class EntryListView(ListView):
    model = models.Entry
    template_name = 'punchcard/entry/list.html'
    queryset = models.Entry.objects.all().order_by('-date', 'category')

class EntryAddView(CreateView):
    model = models.Entry
    form_class = forms.EntryForm
    template_name = 'punchcard/entry/add.html'

class EntryDetailView(DetailView):
    model = models.Entry
    template_name = 'punchcard/entry/detail.html'

class EntryEditView(UpdateView):
    model = models.Entry
    form_class = forms.EntryForm
    template_name = 'punchcard/entry/edit.html'

#TODO: Delete Entry


#################### Categories ####################

class CategoryListView(ListView):
    model = models.Category
    template_name = 'punchcard/category/list.html'
    # Toplevel categories are queried, the template recurses to children
    queryset = models.Category.objects.filter(parent=None)

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        context['show_inactive'] = 'show_inactive' in self.request.GET
        return context

class CategoryAddView(CreateView):
    model = models.Category
    form_class = forms.CategoryAddForm
    template_name = 'punchcard/category/add.html'

class CategoryDetailView(DetailView):
    model = models.Category
    template_name = 'punchcard/category/detail.html'

class CategoryEditView(UpdateView):
    model = models.Category
    form_class = forms.CategoryForm
    template_name = 'punchcard/category/edit.html'

#TODO: Delete Category


#################### Reports ####################

class ReportWeeklyListView(TemplateView):
    template_name = 'punchcard/report/weekly_list.html'
    default_n_weeks = 2

    def get_context_data(self, **kwargs):
        context = super(ReportWeeklyListView, self).get_context_data(**kwargs)

        n_weeks = self.request.GET.get('n_weeks', self.default_n_weeks)
        try:
            n_weeks = int(n_weeks)
        except ValueError:
            n_weeks = self.default_n_weeks
        if n_weeks < 1: n_weeks = self.default_n_weeks

        target_day = None
        if 'target_day' in self.request.GET:
            try:
                target_day = dateutils.date_from_str(self.request.GET['target_day'])
            except ValueError: pass
        if target_day is None:
            target_day = date.today()

        weeks = dateutils.get_recent_weeks(n_weeks, target_day)[::-1]

        start_date = weeks[-1][0]
        end_date = weeks[0][-1]

        context['n_weeks'] = n_weeks
        context['target_day'] = target_day
        context['today'] = date.today()
        context['weeks'] = imap(self._get_week_info, weeks)
        return context

    def _get_week_info(self, days):
        '''
        Returns a datastructure for the week in the form of:
            {
                'start_date':
                'end_date':
                'first_day': <same as first item in 'days'>,
                'days': {
                    <datetime.date object>: {
                        'date':
                        'weekday_name':
                        'category_hours': {
                            <category1>: <hours1>,
                            <category2>: <hours2>,
                            ...
                        }
                        'entries': [
                            <entry1>,
                            <entry2>,
                            ...
                        ]
                    }
                    ...
                }
                'category_hours': {
                    <category1>: <hours1>,
                    <category2>: <hours2>,
                    ...
                }
            }
        '''

        entries = models.Entry.objects.filter(date__gte=days[0], date__lte=days[-1])

        days_info = {day: {
            'date': day,
            'weekday_name': day.strftime("%A"),
            'category_hours': defaultdict(lambda: 0),
            'entries': [],
        } for day in days}

        category_hours = defaultdict(lambda: 0)
        for entry in entries:
            category_hours[entry.category] += entry.hours
            days_info[entry.date]['category_hours'][entry.category] += entry.hours
            days_info[entry.date]['entries'].append(entry)

        # Convert defaultdict to dict
        for info in days_info.itervalues():
            info['category_hours'] = dict(info['category_hours'])

        ret = {
            'start_date': days[0],
            'end_date': days[-1],
            'category_hours': dict(category_hours),
            'days': sorted(days_info.itervalues(), key=lambda x: x['date']),
        }
        ret['first_day'] = ret['days'][0]
        return ret
