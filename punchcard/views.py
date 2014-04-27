from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView

from punchcard import models, forms


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
