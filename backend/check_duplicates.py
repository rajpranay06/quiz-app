#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to check for duplicate quiz titles in the database.
"""
import os
import sys
import django

print("Starting script...")

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

print("Django set up successfully.")

from base.models import Quiz
from collections import Counter

def find_duplicate_quiz_titles():
    """Find and print any duplicate quiz titles in the database."""
    print("Fetching all quizzes from database...")
    all_quizzes = Quiz.objects.all()
    print(f"Found {len(all_quizzes)} quizzes total")
    
    all_titles = [quiz.title for quiz in all_quizzes]
    title_counts = Counter(all_titles)
    
    print(f"Title counts: {dict(title_counts)}")
    
    duplicates = {title: count for title, count in title_counts.items() if count > 1}
    
    if duplicates:
        print("Found duplicate quiz titles:")
        for title, count in duplicates.items():
            print(f"  - '{title}' appears {count} times")
            # Print the IDs of the duplicate quizzes
            quizzes = Quiz.objects.filter(title=title)
            for quiz in quizzes:
                print(f"    Quiz ID: {quiz.id}, Created by: {quiz.creator.username}, Created at: {quiz.created_at}")
        
        print("\nTo fix duplicate quiz titles, you can either:")
        print("1. Manually update the titles through the Django admin")
        print("2. Run a database query to append IDs to duplicate titles")
        print("3. Delete one of the duplicate quizzes if not needed")
    else:
        print("No duplicate quiz titles found!")

if __name__ == "__main__":
    try:
        find_duplicate_quiz_titles()
        print("Script completed successfully.")
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
