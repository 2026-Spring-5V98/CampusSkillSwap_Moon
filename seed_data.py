import os
import django
import random

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_skillswap.settings')
django.setup()

from django.contrib.auth.models import User
from MainApp.models import Skill, Review

def create_seed_data():
    print("🌱 Starting data seeding...")

    # 1. Create 5 Users
    usernames = ['alex_dev', 'sarah_art', 'mike_tutor', 'emily_write', 'jake_photo']
    users = []
    for username in usernames:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@example.com',
                'first_name': username.split('_')[0].capitalize(),
                'last_name': 'Student'
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            print(f"✅ Created user: {username}")
        users.append(user)

    # 2. Create Skills for each user
    skill_data = [
        ('Python Programming', 'tech', 'I can help you with Python basics, Django, and data analysis.', False, 25.00),
        ('Web Design Basics', 'design', 'Learn how to create beautiful websites using HTML and CSS.', True, 0),
        ('Calculus Tutoring', 'tutoring', 'Expert help with Calculus I and II. I simplify complex topics.', False, 20.00),
        ('Academic Writing', 'writing', 'I can proofread your essays and help with citations.', False, 15.00),
        ('Portrait Photography', 'other', 'Professional portraits for your LinkedIn or social media.', False, 40.00),
        ('Guitar Lessons', 'music', 'Beginner to intermediate acoustic guitar lessons.', True, 0),
        ('Spanish Conversation', 'language', 'Practice speaking Spanish with a native speaker.', True, 0),
    ]

    skills = []
    for i, (title, cat, desc, free, price) in enumerate(skill_data):
        owner = users[i % len(users)]
        skill, created = Skill.objects.get_or_create(
            title=title,
            owner=owner,
            defaults={
                'category': cat,
                'description': desc,
                'is_free': free,
                'price': price,
                'availability': 'available'
            }
        )
        if created:
            print(f"✅ Created skill: {title} by {owner.username}")
        skills.append(skill)

    # 3. Create Reviews (Rating System)
    comments = [
        "Amazing tutor! Very patient and explains things clearly.",
        "Great session, I learned so much in just one hour.",
        "Highly recommend! Very professional and knowledgeable.",
        "Friendly and helpful. Exactly what I needed for my project.",
        "Fantastic experience. Will definitely book again!"
    ]

    for skill in skills:
        # Each skill gets 2-3 reviews from different users (not the owner)
        potential_reviewers = [u for u in users if u != skill.owner]
        reviewers = random.sample(potential_reviewers, random.randint(2, 3))
        
        for reviewer in reviewers:
            review, created = Review.objects.get_or_create(
                skill=skill,
                user=reviewer,
                defaults={
                    'rating': random.randint(4, 5), # High ratings for better demo data
                    'comment': random.choice(comments)
                }
            )
            if created:
                print(f"⭐ Added {review.rating}-star review for '{skill.title}' by {reviewer.username}")

    print("✨ Seeding complete!")

if __name__ == '__main__':
    create_seed_data()
