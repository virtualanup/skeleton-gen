from django.contrib import admin

from .models import SourceSentence, ProcessedSkeleton, Skeleton

@admin.register(SourceSentence)
class SentenceAdmin(admin.ModelAdmin):
    search_fields = ['sentence']
    list_display = ['sentence', 'trips_parse', 'word_map']

@admin.register(ProcessedSkeleton)
class ProcessedSkeletonAdmin(admin.ModelAdmin):
    search_fields = ['sentence']
    list_display = ['sentence', 'skeleton', 'possible_entries', 'skeleton_type']

@admin.register(Skeleton)
class SkeletonAdmin(admin.ModelAdmin):
    list_display = ['skeleton']


