from itertools import imap

from django.db import models
from django.core.urlresolvers import reverse


class Entry(models.Model):
    '''A log of work accomplished.'''
    category = models.ForeignKey('Category')
    date = models.DateField()
    hours = models.FloatField()
    description = models.TextField()

    class Meta:
        verbose_name_plural = 'Entries'

    def get_absolute_url(self):
        return reverse('entry_detail', args=[str(self.id)])


class Category(models.Model):
    '''A category of entries.

    Could be a project or a hobby the user wants to keep track of. Categories
    can be nested inside other categories using the parent field, which is NULL
    for top level categories. If a category has active=False, it will not show
    up on the category listing and new entries cannot use it, but its related
    entries are still stored.
    '''
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    parent = models.ForeignKey('Category', related_name='children', null=True,
                               blank=True, db_index=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Categories'

    class CategoryTreeLoop(Exception):
        """Loop in category tree."""
        ERROR_STR = "Category tree forms a loop."
        def __init__(self, *args, **kwargs):
            super(CategoryTreeLoop).__init__(self, ERROR_STR, *args, **kwargs)

    def __unicode__(self):
        return self.full_path

    @property
    def full_path(self):
        '''
        A string representatin of the path of this category, starting at a
        top level category and walking the tree until this category is reached.
        '''
        #TODO: This is very inefficient right now.
        #      In the future I want to store full_path in the database and only
        #      update it when needed.
        categories = self._get_ancestors()
        category_names = imap(lambda c: c.name, categories)
        return ' / '.join(category_names)

    def _get_ancestors(self):
        '''
        Returns a list of categories starting from the top level category and
        ending at this category.
        '''
        cat_list = [self]
        cat_id_list = [self.id]
        current = self
        while current.parent_id:
            if current.parent_id in cat_id_list:
                raise Category.TreeLoopError("There was a loop in the category tree")
            current = current.parent
            cat_list.insert(0, current)
            cat_id_list.insert(0, current.id)
        return cat_list

    def get_valid_parents(self):
        """
        Returns a set of possible parents that would not produce a loop in the
        category tree.
        """
        #TODO: This is very inefficient right now
        #      In the future I want to store a full path in the database, and
        #      get the valid parents list in a single query without
        #      postprocessing

        # Blacklist all descendents of this category
        blacklisted = set([self])
        blacklist_size = 0
        while blacklist_size != len(blacklisted):
            blacklist_size = len(blacklisted)
            for category in blacklisted:
                blacklisted = blacklisted.union(category.children.filter(active=True))
                blacklist_grew = True

        # Subtract blacklisted categories from all possible ones
        queryset = Category.objects.exclude(id__exact=self.id).filter(active=True)
        categories = set(queryset)
        return set(queryset).difference(blacklisted)

    def get_absolute_url(self):
        return reverse('category_detail', args=[str(self.id)])
