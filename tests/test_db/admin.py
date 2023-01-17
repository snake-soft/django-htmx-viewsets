from django.contrib import admin
from . import models


'''
Tag
Attribute inline
child
'''

class ChildInline(admin.TabularInline):
    model = models.Child


class AttributeValuesInline(admin.TabularInline):
    model = models.AttributeValue


class MainAdmin(admin.ModelAdmin):
    inlines = [ChildInline, AttributeValuesInline]
    filter_horizontal = ['tags']


admin.site.register(models.Parent)
admin.site.register(models.Tag)
admin.site.register(models.Main, MainAdmin)
