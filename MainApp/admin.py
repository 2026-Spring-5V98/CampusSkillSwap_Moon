from django.contrib import admin
from .models import Skill, Review


class SkillAdmin(admin.ModelAdmin):
    """
    Custom admin interface for the Skill model.
    Makes it easier to manage skills from the Django admin panel.
    """
    # Columns to display in the list view
    list_display = ('title', 'owner', 'category', 'availability', 'price', 'created_at')
    
    # Add filters on the right sidebar
    list_filter = ('category', 'availability', 'is_free', 'created_at')
    
    # Add search functionality
    search_fields = ('title', 'description', 'owner__username')
    
    # Group related fields together for better organization
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'category', 'owner')
        }),
        ('Pricing', {
            'fields': ('is_free', 'price')
        }),
        ('Contact & Availability', {
            'fields': ('contact_preference', 'availability')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Hide by default
        }),
    )
    
    # Make timestamps read-only (they're auto-generated)
    readonly_fields = ('created_at', 'updated_at')
    
    # Sort by newest first
    ordering = ('-created_at',)


class ReviewAdmin(admin.ModelAdmin):
    """Custom admin interface for the Review model."""
    list_display = ('skill', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('skill__title', 'user__username', 'comment')
    readonly_fields = ('created_at',)


# Register the models
admin.site.register(Skill, SkillAdmin)
admin.site.register(Review, ReviewAdmin)
