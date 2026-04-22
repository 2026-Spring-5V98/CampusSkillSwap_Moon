from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Skill, Booking
from django.db.models import Q
from .forms import UserRegistrationForm, SkillForm, ReviewForm, BookingForm

def search_skills(request):
    """
    Simple function-based view for searching skills.
    Searches by title or category based on the 'q' parameter.
    """
    query = request.GET.get('q', '')
    results = []
    
    if query:
        # Search for the query string in title OR category
        results = Skill.objects.filter(
            Q(title__icontains=query) | 
            Q(category__icontains=query)
        ).distinct()
    
    context = {
        'query': query,
        'skills': results,
    }
    return render(request, 'MainApp/skill_list.html', context)


class HomeView(ListView):
    """
    Display the home page with all available skills.
    Shows 12 skills per page with pagination.
    """
    model = Skill
    template_name = 'MainApp/home.html'
    context_object_name = 'skills'
    paginate_by = 12


class SkillListView(ListView):
    """
    Display all skills in a list view with filters.
    Users can browse all available skills.
    """
    model = Skill
    template_name = 'MainApp/skill_list.html'
    context_object_name = 'skills'
    paginate_by = 12
    
    def get_queryset(self):
        """Filter skills based on category if provided."""
        queryset = Skill.objects.all()
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        return queryset


class SkillDetailView(DetailView):
    """
    Display details of a single skill.
    Shows the full description and contact information for the skill owner.
    Now also handles review display and submission.
    """
    model = Skill
    template_name = 'MainApp/skill_detail.html'
    context_object_name = 'skill'

    def get_context_data(self, **kwargs):
        """Include the review form in context."""
        context = super().get_context_data(**kwargs)
        context['review_form'] = ReviewForm()
        # Check if current user has already reviewed this skill
        if self.request.user.is_authenticated:
            context['user_has_reviewed'] = self.object.reviews.filter(user=self.request.user).exists()
        return context

    def post(self, request, *args, **kwargs):
        """Handle review submission."""
        if not request.user.is_authenticated:
            return redirect('login')
            
        self.object = self.get_object()
        
        # Don't allow owner to review their own skill
        if self.object.owner == request.user:
            messages.error(request, "You cannot review your own skill.")
            return redirect('skill_detail', pk=self.object.pk)

        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.skill = self.object
            review.user = request.user
            try:
                review.save()
                messages.success(request, "Thank you for your review!")
            except:
                messages.error(request, "You have already reviewed this skill.")
        
        return redirect('skill_detail', pk=self.object.pk)


class SkillCreateView(LoginRequiredMixin, CreateView):
    """
    Allow logged-in users to create a new skill post.
    Requires user to be logged in (LoginRequiredMixin handles this).
    Redirects to dashboard after successful creation.
    """
    model = Skill
    form_class = SkillForm
    template_name = 'MainApp/skill_form.html'
    success_url = reverse_lazy('dashboard')
    
    def form_valid(self, form):
        """
        Save the form and set the owner to the current user.
        Called when the form is valid before saving.
        """
        form.instance.owner = self.request.user
        messages.success(self.request, 'Skill created successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Show error message if form is invalid."""
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class SkillUpdateView(LoginRequiredMixin, UpdateView):
    """
    Allow users to edit their own skill posts.
    Users can only edit skills they own.
    """
    model = Skill
    form_class = SkillForm
    template_name = 'MainApp/skill_form.html'
    success_url = reverse_lazy('dashboard')
    
    def get_object(self, queryset=None):
        """Retrieve the skill and check ownership."""
        obj = super().get_object(queryset)
        # Only allow the owner to edit
        if obj.owner != self.request.user:
            raise PermissionDenied('You can only edit your own skills.')
        return obj
    
    def form_valid(self, form):
        """Show success message when skill is updated."""
        messages.success(self.request, 'Skill updated successfully!')
        return super().form_valid(form)


class SkillDeleteView(LoginRequiredMixin, DeleteView):
    """
    Allow users to delete their own skill posts.
    Requires confirmation before deletion.
    """
    model = Skill
    template_name = 'MainApp/skill_confirm_delete.html'
    success_url = reverse_lazy('dashboard')
    
    def get_object(self, queryset=None):
        """Retrieve the skill and check ownership."""
        obj = super().get_object(queryset)
        # Only allow the owner to delete
        if obj.owner != self.request.user:
            raise PermissionDenied('You can only delete your own skills.')
        return obj
    
    def delete(self, request, *args, **kwargs):
        """Show success message when skill is deleted."""
        messages.success(request, 'Skill deleted successfully!')
        return super().delete(request, *args, **kwargs)


class DashboardView(LoginRequiredMixin, View):
    """
    Show the user's dashboard with their skills and session requests.
    """
    def get(self, request):
        user_skills = Skill.objects.filter(owner=request.user)
        # Bookings made BY the user (Outgoing)
        my_requests = Booking.objects.filter(student=request.user)
        # Bookings for skills OWNED BY the user (Incoming)
        incoming_requests = Booking.objects.filter(skill__owner=request.user)
        
        context = {
            'user_skills': user_skills,
            'skill_count': user_skills.count(),
            'my_requests': my_requests,
            'incoming_requests': incoming_requests,
        }
        return render(request, 'MainApp/dashboard.html', context)


class RequestSessionView(LoginRequiredMixin, CreateView):
    """Allow students to request a session for a skill."""
    model = Booking
    form_class = BookingForm
    template_name = 'MainApp/booking_form.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        skill = get_object_or_404(Skill, pk=self.kwargs['pk'])
        if skill.owner == self.request.user:
            messages.error(self.request, "You cannot request your own skill.")
            return redirect('skill_detail', pk=skill.pk)
            
        form.instance.skill = skill
        form.instance.student = self.request.user
        messages.success(self.request, "Session request transmitted to the instructor.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['skill'] = get_object_or_404(Skill, pk=self.kwargs['pk'])
        return context


class UpdateBookingStatusView(LoginRequiredMixin, View):
    """Allow instructors to accept or reject requests."""
    def post(self, request, pk, status):
        booking = get_object_or_404(Booking, pk=pk)
        if booking.skill.owner != request.user:
            raise PermissionDenied
            
        if status in ['accepted', 'rejected', 'completed']:
            booking.status = status
            booking.save()
            messages.success(request, f"Request status updated to {status}.")
            
        return redirect('dashboard')


class UserRegistrationView(View):
    """
    Handle user registration.
    Allows new users to create an account.
    """
    def get(self, request):
        """Display the registration form."""
        if request.user.is_authenticated:
            # Redirect to dashboard if already logged in
            return redirect('dashboard')
        form = UserRegistrationForm()
        return render(request, 'MainApp/register.html', {'form': form})
    
    def post(self, request):
        """Process the registration form."""
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Create the new user
            user = form.save()
            # Log the user in immediately after registration
            login(request, user)
            messages.success(request, f'Welcome {user.username}! Your account has been created.')
            return redirect('dashboard')
        else:
            # Show form errors
            messages.error(request, 'Please correct the errors below.')
        return render(request, 'MainApp/register.html', {'form': form})


class UserLoginView(View):
    """
    Handle user login.
    Allows registered users to log in.
    """
    def get(self, request):
        """Display the login form."""
        if request.user.is_authenticated:
            # Redirect to dashboard if already logged in
            return redirect('dashboard')
        return render(request, 'MainApp/login.html')
    
    def post(self, request):
        """Process the login form."""
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Login successful
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            # Redirect to 'next' if provided, otherwise go to dashboard
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            # Authentication failed
            messages.error(request, 'Invalid username or password.')
        return render(request, 'MainApp/login.html')


class UserLogoutView(View):
    """
    Handle user logout.
    Logs out the current user and redirects to home.
    """
    def get(self, request):
        """Log out the user."""
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('home')
