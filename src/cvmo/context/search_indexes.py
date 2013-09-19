from haystack import indexes
from cvmo.context.models import *

class ContextDefinitionIndex(indexes.SearchIndex, indexes.Indexable):
	text = indexes.NgramField(document=True, use_template=True)
        name = indexes.CharField(model_attr='name')

        content_auto = indexes.EdgeNgramField(model_attr='name')

    	def get_model(self):
    		return ContextDefinition

    	def index_queryset(self, using=None):
    		return self.get_model().objects.all()