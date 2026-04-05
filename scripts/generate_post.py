"""
FitnessDailyTips Auto Post Generator
Generates SEO-optimized fitness articles using OpenAI GPT API
and commits them to the blog repository.
"""

from openai import OpenAI
import datetime
import os
import random
import re

# High CPC keyword categories for fitness
TOPIC_POOLS = {
    "workout": [
        "Best 20-Minute Home Workouts for Busy People",
        "Full Body Workout Routine for Beginners in {year}",
        "{number} Best Exercises You Can Do Without Equipment",
        "How to Create Your Own Workout Plan in {year}",
        "Best Morning Workout Routine to Start Your Day",
        "The Ultimate Push Pull Legs Workout Split Guide",
        "{number}-Day Workout Plan for Maximum Results",
    ],
    "weight_loss": [
        "How to Lose Weight Without Starving Yourself",
        "{number} Science-Backed Ways to Lose Belly Fat",
        "Best Exercises for Weight Loss at Home in {year}",
        "How to Break Through a Weight Loss Plateau",
        "Walking for Weight Loss: How Many Steps You Really Need",
        "Why You Are Not Losing Weight Despite Working Out",
        "How to Lose {number} Pounds in a Month Safely",
    ],
    "muscle_building": [
        "How to Build Muscle Without a Gym",
        "Best Protein Sources for Muscle Growth in {year}",
        "{number} Muscle Building Mistakes Beginners Make",
        "How Long Does It Take to Build Noticeable Muscle",
        "Best Exercises for Bigger Arms at Home",
        "How to Build a Bigger Chest with Push-Ups",
        "Progressive Overload: The Key to Building Muscle",
    ],
    "cardio": [
        "HIIT vs Steady State Cardio: Which Burns More Fat",
        "Beginner Running Plan: Couch to 5K Guide {year}",
        "Best Cardio Exercises That Don't Involve Running",
        "How to Improve Your Running Endurance in {number} Weeks",
        "Jump Rope Workout: The Best Cardio You Are Not Doing",
        "{number}-Minute Cardio Workouts You Can Do Anywhere",
        "How to Start Running When You Are Out of Shape",
    ],
    "nutrition": [
        "What to Eat Before and After a Workout",
        "Best High Protein Meals for Muscle Recovery",
        "How Much Protein Do You Really Need Per Day",
        "{number} Healthy Meal Prep Ideas for the Week",
        "Best Pre-Workout Foods for Energy and Performance",
        "How to Count Macros: A Beginner Guide for {year}",
        "Best Supplements for Gym Beginners in {year}",
    ],
    "stretching": [
        "Best Stretches to Do Every Morning for Flexibility",
        "How to Improve Your Flexibility in {number} Weeks",
        "Best Cool Down Stretches After a Workout",
        "How to Do a Proper Push-Up with Perfect Form",
        "Yoga vs Stretching: Which Is Better for Recovery",
        "{number} Stretches to Relieve Lower Back Pain",
        "Best Mobility Exercises for Desk Workers in {year}",
    ],
    "home_gym": [
        "How to Build a Home Gym on a Budget in {year}",
        "Best Home Gym Equipment Under $100",
        "{number} Best Resistance Band Exercises for Full Body",
        "Dumbbell Only Workout: Complete Home Training Guide",
        "Best Adjustable Dumbbells Compared {year}",
        "How to Get Fit at Home Without Any Equipment",
        "Kettlebell Workout: {number} Best Exercises for Beginners",
    ],
}

SYSTEM_PROMPT = """You are an expert fitness writer for a blog called FitnessDailyTips.
Write SEO-optimized, informative, and engaging blog posts about fitness and exercise.

Rules:
- Write in a friendly, motivational but authoritative tone
- Use short paragraphs (2-3 sentences max)
- Include practical, actionable advice
- Use headers (##) to break up sections
- Include bullet points and numbered lists where appropriate
- Write between 1200-1800 words
- Naturally include the main keyword 3-5 times
- Include a compelling introduction that hooks the reader
- End with a clear conclusion/call-to-action
- Do NOT include any AI disclaimers or mentions of being AI-generated
- Write as if you are a certified personal trainer sharing expertise
- Make content evergreen where possible
- Include specific numbers, sets, reps, and examples
- Do NOT use markdown title (# Title) - just start with the content
"""


def pick_topic():
    """Select a random topic from the pools."""
    year = datetime.datetime.now().year
    number = random.choice([3, 5, 7, 10, 12, 15])
    category = random.choice(list(TOPIC_POOLS.keys()))
    title_template = random.choice(TOPIC_POOLS[category])
    title = title_template.format(year=year, number=number)
    return title, category


def generate_post_content(title, category):
    """Generate a blog post using OpenAI GPT API."""
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=4000,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Write a comprehensive blog post with the title: \"{title}\"\n\nCategory: {category.replace('_', ' ')}\n\nRemember to write 1200-1800 words, use ## for section headers, and make it SEO-friendly.",
            },
        ],
    )

    return response.choices[0].message.content


def slugify(title):
    """Convert title to URL-friendly slug."""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    return slug


def get_repo_root():
    """Get the repository root directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(script_dir)


def get_existing_titles():
    """Get titles of existing posts to avoid duplicates."""
    posts_dir = os.path.join(get_repo_root(), '_posts')
    titles = set()
    if os.path.exists(posts_dir):
        for filename in os.listdir(posts_dir):
            if filename.endswith('.md'):
                title_part = filename[11:-3]
                titles.add(title_part)
    return titles


def create_post():
    """Generate and save a new blog post."""
    existing = get_existing_titles()

    # Try up to 10 times to find a non-duplicate topic
    for _ in range(10):
        title, category = pick_topic()
        slug = slugify(title)
        if slug not in existing:
            break
    else:
        # If all attempts hit duplicates, add a random suffix
        title, category = pick_topic()
        slug = slugify(title) + f"-{random.randint(100, 999)}"

    print(f"Generating post: {title}")
    print(f"Category: {category}")

    content = generate_post_content(title, category)

    # Create the post file
    today = datetime.datetime.now()
    date_str = today.strftime('%Y-%m-%d')
    filename = f"{date_str}-{slug}.md"

    posts_dir = os.path.join(get_repo_root(), '_posts')
    os.makedirs(posts_dir, exist_ok=True)

    filepath = os.path.join(posts_dir, filename)

    # Create frontmatter
    frontmatter = f"""---
layout: post
title: "{title}"
date: {today.strftime('%Y-%m-%d %H:%M:%S')} +0000
categories: [{category.replace('_', '-')}]
description: "{title} - Expert fitness tips and workout advice to help you reach your goals."
---

{content}
"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(frontmatter)

    print(f"Post saved: {filepath}")
    return filepath, filename


if __name__ == '__main__':
    filepath, filename = create_post()
    print(f"Done! Post generated: {filename}")
