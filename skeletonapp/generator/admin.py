from django.contrib import admin

from .models import SourceSentence, ProcessedSkeleton

@admin.register(SourceSentence)
class SentenceAdmin(admin.ModelAdmin):
    search_fields = ['sentence']
    list_display = ['sentence', 'trips_parse', 'word_map']

@admin.register(ProcessedSkeleton)
class ProcessedSkeletonAdmin(admin.ModelAdmin):
    search_fields = ['sentence']
    list_display = ['sentence', 'skeleton', 'trips_parse', 'skeleton_type']
