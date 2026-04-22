from django.db import models
from django.contrib.auth.models import User

# Category choices for skills
CATEGORY_CHOICES = [
    ('tutoring', 'Tutoring'),
    ('tech', 'Tech & Programming'),
    ('design', 'Design'),
    ('writing', 'Writing & Editing'),
    ('music', 'Music & Arts'),
    ('fitness', 'Fitness & Sports'),
    ('language', 'Language Exchange'),
    ('professional', 'Professional Services'),
    ('other', 'Other'),
]

# Availability status choices
AVAILABILITY_CHOICES = [
    ('available', 'Available'),
    ('unavailable', 'Unavailable'),
    ('busy', 'Busy'),
]

# Contact preference choices
CONTACT_CHOICES = [
    ('email', 'Email'),
    ('phone', 'Phone'),
    ('in_person', 'In Person'),
    ('online', 'Online'),
]


class Skill(models.Model):
    """
    Skill model represents a service/skill that a student offers.
    Each skill is linked to a user (the person offering the skill).
    """
    # Owner of the skill (the student offering it)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skills')
    
    # Basic information about the skill
    title = models.CharField(max_length=200, help_text="Title of the skill or service")
    description = models.TextField(help_text="Detailed description of what you offer")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    
    # Pricing information
    is_free = models.BooleanField(default=False, help_text="Check if you offer this for free")
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, 
                                help_text="Price per session/service (leave blank if free)")
    
    # Contact and availability
    contact_preference = models.CharField(max_length=50, choices=CONTACT_CHOICES, default='email')
    availability = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, default='available')
    
    # Timestamps - used to track when the skill was created/updated
    created_at = models.DateTimeField(auto_now_add=True)  # Auto-set when created
    updated_at = models.DateTimeField(auto_now=True)      # Auto-updated when modified
    
    class Meta:
        # Show newest skills first in the default ordering
        ordering = ['-created_at']
    
    def __str__(self):
        """Display string for the skill (appears in admin and templates)"""
        return f"{self.title} by {self.owner.get_full_name() or self.owner.username}"


class Review(models.Model):
    """
    Review model allows students to rate and comment on skills.
    Each review is linked to a skill and a user.
    """
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevent multiple reviews from the same user on the same skill
        unique_together = ('skill', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"Review for {self.skill.title} by {self.user.username}"


class Booking(models.Model):
    """
    Booking model tracks requests for skills between students and instructors.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='bookings')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings_made')
    message = models.TextField(help_text="Introduce yourself and explain what you want to learn.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Request for {self.skill.title} by {self.student.username}"
