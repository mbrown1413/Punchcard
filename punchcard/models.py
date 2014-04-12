from itertools import imap

from django.db import models
from django.core.urlresolvers import reverse


class Entry(models.Model):
    category = models.ForeignKey('Category')
    date = models.DateField()
    hours = models.FloatField()
    description = models.TextField()

    class Meta:
        verbose_name_plural = 'Entries'

    def get_absolute_url(self):
        return reverse('entry_detail', args=[str(self.id)])


class Category(models.Model):
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
        try:
            return self.full_path
        except Exception as e:
            import pdb; pdb.set_trace()

    @property
    def full_path(self):
        #TODO: This is very inefficient right now.
        #      In the future I want to store full_path in the database and only
        #      update it when needed.
        categories = self._get_ancestors()
        category_names = imap(lambda c: c.name, categories)
        return ' / '.join(category_names)

    def _get_ancestors(self):
        '''
        Returns a list starting from the top level category and ending at this
        category.
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
        Returns a set of parents that would not produce a loop in the category
        tree.
        """
        #TODO: This is very inefficient right now
        #      In the future I want to store a full path in the database, and
        #      get the valid parents list in a single query without
        #      postprocessing
        queryset = Category.objects.exclude(id__exact=self.id).filter(active=True)

        categories = set(queryset)
        blacklisted = set([self])
        blacklist_size = 0
        while blacklist_size != len(blacklisted):
            blacklist_size = len(blacklisted)
            for category in blacklisted:
                blacklisted = blacklisted.union(category.children.filter(active=True))
                blacklist_grew = True
        return categories.difference(blacklisted)

    def get_absolute_url(self):
        return reverse('category_detail', args=[str(self.id)])
