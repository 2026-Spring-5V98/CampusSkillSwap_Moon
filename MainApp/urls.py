from django.urls import path
from . import views

# URL patterns for MainApp
# Pattern: path('url/', view_name, name='url_name')

urlpatterns = [
    # Home page - shows all skills
    path('', views.HomeView.as_view(), name='home'),
    
    # Skills browsing
    path('skills/', views.SkillListView.as_view(), name='skill_list'),
    path('skills/<int:pk>/', views.SkillDetailView.as_view(), name='skill_detail'),
    
    # Skill management (CRUD operations)
    path('skills/create/', views.SkillCreateView.as_view(), name='skill_create'),
    path('skills/<int:pk>/edit/', views.SkillUpdateView.as_view(), name='skill_edit'),
    path('skills/<int:pk>/delete/', views.SkillDeleteView.as_view(), name='skill_delete'),
    path('search/', views.search_skills, name='skill_search'),
    
    # Session Requests (Bookings)
    path('skills/<int:pk>/request/', views.RequestSessionView.as_view(), name='skill_request'),
    path('bookings/<int:pk>/update/<str:status>/', views.UpdateBookingStatusView.as_view(), name='booking_update'),
    
    # User dashboard - shows user's own skills
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # Authentication URLs
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
]
