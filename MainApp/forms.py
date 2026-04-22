from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Skill, Review, Booking, CATEGORY_CHOICES, CONTACT_CHOICES, AVAILABILITY_CHOICES


class UserRegistrationForm(UserCreationForm):
    """
    Form for user registration.
    Extends Django's built-in UserCreationForm to include additional fields.
    """
    # Email field - required for account creation
    email = forms.EmailField(required=True, help_text='Required. Enter a valid email address.')
    
    # First and last name fields for better user profiles
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=150, required=False, help_text='Optional.')
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
    
    def clean_email(self):
        """
        Validate that the email is not already registered.
        This prevents duplicate email accounts.
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email
    
    def save(self, commit=True):
        """Save the user with the email field populated."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class SkillForm(forms.ModelForm):
    """
    Form for creating and editing skill posts.
    This form is used when users want to add a new skill or modify an existing one.
    """
    
    # Override the category field to use radio buttons for better UX
    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        widget=forms.RadioSelect,
        help_text='Select the category that best describes your skill.'
    )
    
    # Override contact preference with radio buttons
    contact_preference = forms.ChoiceField(
        choices=CONTACT_CHOICES,
        widget=forms.RadioSelect,
        help_text='How would you prefer people to contact you?'
    )
    
    # Override availability with radio buttons
    availability = forms.ChoiceField(
        choices=AVAILABILITY_CHOICES,
        widget=forms.RadioSelect,
        help_text='Set your current availability status.'
    )
    
    class Meta:
        model = Skill
        # These are the fields that users can edit (owner is auto-set in views)
        fields = ('title', 'description', 'category', 'is_free', 'price', 
                  'contact_preference', 'availability')
        
        # Customize how each field appears on the form
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Python Programming Tutor'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe your skill, experience, and what you can offer...',
                'rows': 5
            }),
            'is_free': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
        }
    
    def clean(self):
        """
        Validate that price is set if is_free is False.
        This prevents users from forgetting to set a price.
        """
        cleaned_data = super().clean()
        is_free = cleaned_data.get('is_free')
        price = cleaned_data.get('price')
        
        # If it's not free, price must be provided and greater than 0
        if not is_free and not (price is not None and price > 0):
            raise forms.ValidationError(
                'Please set a price or mark this skill as free.'
            )
        
        # If it's free, price should be 0
        if is_free and price and price > 0:
            cleaned_data['price'] = 0
        
        return cleaned_data


class ReviewForm(forms.ModelForm):
    """Form for users to leave a review."""
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Write your review here...'
            }),
        }


class BookingForm(forms.ModelForm):
    """
    Form for students to request a session.
    """
    class Meta:
        model = Booking
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Hi! I am interested in learning this skill because...'
            }),
        }
