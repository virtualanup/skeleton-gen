from django.contrib import admin

from .models import SourceSentence

@admin.register(SourceSentence)
class SentenceAdmin(admin.ModelAdmin):
    search_fields = ['sentence']
    list_display = ['sentence', 'trips_parse', 'word_map']
