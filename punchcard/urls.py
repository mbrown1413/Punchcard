from django.conf.urls import patterns, include, url

from punchcard.views import EntryListView, EntryAddView, EntryDetailView, EntryEditView
from punchcard.views import CategoryListView, CategoryAddView, CategoryDetailView, CategoryEditView

urlpatterns = patterns('',

    # Entries
    url(r'^entries/$', EntryListView.as_view(), name='entry_list'),
    url(r'^entries/add/$', EntryAddView.as_view(), name='entry_add'),
    url(r'^entries/(?P<pk>\d+)/$', EntryDetailView.as_view(), name='entry_detail'),
    url(r'^entries/(?P<pk>\d+)/edit/$', EntryEditView.as_view(), name='entry_edit'),

    # Categories
    url(r'^categories/$', CategoryListView.as_view(), name='category_list'),
    url(r'^categories/add$', CategoryAddView.as_view(), name='category_add'),
    url(r'^categories/(?P<pk>\d+)/$', CategoryDetailView.as_view(), name='category_detail'),
    url(r'^categories/(?P<pk>\d+)/edit/$', CategoryEditView.as_view(), name='category_edit'),

    url(r'^$', EntryListView.as_view()),

)
