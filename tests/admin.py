from django.contrib import admin

from .models import TestType, TestOrder, TestCollectionAssignment, TestResult

@admin.register(TestType)
class TestTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'description')  # Display the ID prominently
    search_fields = ('name',)
    list_filter = ('price',)
    ordering = ('id',)  # Order by ID by default

@admin.register(TestOrder)
class TestOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'test_type', 'order_date', 'status', 'collection_time', 'result_sent', 'address')  # Display ID
    search_fields = ('user__username', 'test_type__name')
    list_filter = ('status', 'order_date', 'result_sent')
    ordering = ('-id',)  # Order by ID in descending order
    date_hierarchy = 'order_date'

@admin.register(TestCollectionAssignment)
class TestCollectionAssignmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'test_order', 'collector', 'status', 'collection_date')  # Display ID
    search_fields = ('test_order__id', 'collector__username')
    list_filter = ('status', 'collection_date')
    ordering = ('-id',)  # Order by ID in descending order

@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'test_order', 'result_date', 'result_sent', 'result_file')  # Display ID
    search_fields = ('test_order__id', 'test_order__user__username')
    list_filter = ('result_sent', 'result_date')
    ordering = ('-id',)  # Order by ID in descending order


