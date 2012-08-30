from django.db import models

class PageCategory(models.Model):
    title = models.CharField(max_length=250)
    # Alias is an index for URLs
    alias = models.CharField(max_length=120, db_index=True)
    description = models.TextField(null=True, blank=True)
    # Meta Data in Pickle format
    meta = models.TextField(null=True, blank=True)
    # Parent category
    parent = models.ForeignKey("self", null=True, blank=True)
    
    def __unicode__(self):
        return self.title

class Page(models.Model):
    # Constants
    CONTENT_TYPE_CHOICES = (
        ( "wiki", "Wiki" ),
        ( "html", "HTML" )
    )
    CT_WIKI = "wiki"
    CT_HTML = "html"
    
    title = models.CharField(max_length=250)
    # Alias is an index for URLs
    alias = models.CharField(max_length=120, db_index=True)
    # Intro text is shown in small page descriptions
    intro = models.TextField(null=True, blank=True)
    # This field hosts the contents of the page
    contents = models.TextField()
    # Contents type (e.g.: HTML, wiki markup, etc...)
    contents_type = models.CharField(max_length=120, null=True, blank=True, choices=CONTENT_TYPE_CHOICES)
    # Meta Data in Pickle format
    meta = models.TextField(null=True, blank=True)
    # Amount of visits
    hits = models.IntegerField(null=True, blank=True)
    # Date of creation of page
    created_on = models.DateTimeField(auto_now_add=True)
    # Date of last modification of the page
    last_modfication_on = models.DateTimeField(auto_now=True)
    # Link to categories
    categories = models.ManyToManyField(PageCategory)
    
    def __unicode__(self):
        return self.title
