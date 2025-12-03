"""
Constants and scale explanations for the Mental Health Bot.
"""

# Stress Level Scale (1-10)
STRESS_LEVEL_SCALE = {
    1: "😌 Completely relaxed - No stress at all",
    2: "🙂 Very calm - Minimal tension",
    3: "😊 Calm - Slight awareness of daily tasks",
    4: "😐 Mild stress - Manageable pressure",
    5: "😕 Moderate stress - Noticeable tension",
    6: "😟 Elevated stress - Affecting focus",
    7: "😰 High stress - Difficulty concentrating",
    8: "😫 Very high stress - Overwhelming feelings",
    9: "😨 Severe stress - Significant distress",
    10: "🆘 Extreme stress - Crisis level"
}

# Anxiety Level Scale (1-10)
ANXIETY_LEVEL_SCALE = {
    1: "😌 No anxiety - Completely at ease",
    2: "🙂 Minimal anxiety - Rare worry",
    3: "😊 Low anxiety - Occasional concern",
    4: "😐 Mild anxiety - Some nervousness",
    5: "😕 Moderate anxiety - Frequent worry",
    6: "😟 Elevated anxiety - Persistent unease",
    7: "😰 High anxiety - Interfering with daily life",
    8: "😫 Very high anxiety - Significant impact",
    9: "😨 Severe anxiety - Overwhelming feelings",
    10: "🆘 Extreme anxiety - Panic-level distress"
}

# Mood Rating Scale (1-10)
MOOD_RATING_SCALE = {
    1: "😢 Very low - Deeply sad/depressed",
    2: "😔 Low - Feeling down",
    3: "😕 Below average - Somewhat sad",
    4: "😐 Slightly low - A bit off",
    5: "😶 Neutral - Neither good nor bad",
    6: "🙂 Slightly positive - Okay",
    7: "😊 Good - Pleasant mood",
    8: "😃 Very good - Happy",
    9: "😄 Great - Very happy",
    10: "🤩 Excellent - Euphoric/joyful"
}

# Energy Level Scale (1-10)
ENERGY_LEVEL_SCALE = {
    1: "😴 Exhausted - No energy at all",
    2: "🥱 Very tired - Struggling to stay awake",
    3: "😪 Tired - Low energy",
    4: "😐 Below average - Somewhat fatigued",
    5: "🙂 Moderate - Adequate energy",
    6: "😊 Good - Feeling okay",
    7: "💪 Energetic - Active and alert",
    8: "⚡ Very energetic - Highly active",
    9: "🔥 High energy - Very dynamic",
    10: "🚀 Maximum energy - Unstoppable"
}

# Sweating Level Scale (1-5)
SWEATING_LEVEL_SCALE = {
    1: "💧 None - No sweating",
    2: "💧💧 Minimal - Slight dampness",
    3: "💧💧💧 Moderate - Noticeable sweating",
    4: "💧💧💧💧 Heavy - Significant sweating",
    5: "💧💧💧💧💧 Excessive - Profuse sweating"
}

# Week Rating Scale (1-10)
WEEK_RATING_SCALE = {
    1: "😢 Terrible - Worst week",
    2: "😔 Very bad - Extremely difficult",
    3: "😕 Bad - Challenging week",
    4: "😐 Below average - Some struggles",
    5: "😶 Average - Mixed week",
    6: "🙂 Above average - Mostly okay",
    7: "😊 Good - Pleasant week",
    8: "😃 Very good - Great week",
    9: "😄 Excellent - Wonderful week",
    10: "🤩 Perfect - Best week ever"
}

# Gender Options
GENDER_OPTIONS = [
    ("👨 Male", "male"),
    ("👩 Female", "female"),
    ("🧑 Non-binary", "non_binary"),
    ("🤐 Prefer not to say", "prefer_not_to_say")
]

# Family Status Options
FAMILY_STATUS_OPTIONS = [
    ("💑 Single", "single"),
    ("💏 In a relationship", "relationship"),
    ("💍 Married", "married"),
    ("👨‍👩‍👧 Married with children", "married_with_children"),
    ("💔 Divorced", "divorced"),
    ("🕊️ Widowed", "widowed"),
    ("🤐 Prefer not to say", "prefer_not_to_say")
]

# Physical Activity Options
PHYSICAL_ACTIVITY_OPTIONS = [
    ("🛋️ None", "none"),
    ("🚶 Light (walking, stretching)", "light"),
    ("🏃 Moderate (jogging, cycling)", "moderate"),
    ("🏋️ Intense (gym, sports)", "intense")
]

# Diet Quality Options
DIET_QUALITY_OPTIONS = [
    ("🍔 Poor", "poor"),
    ("🍕 Fair", "fair"),
    ("🥗 Good", "good"),
    ("🥑 Excellent", "excellent")
]

# Smoking Habits Options
SMOKING_HABITS_OPTIONS = [
    ("🚭 Never smoked", "never"),
    ("✋ Former smoker", "former"),
    ("🚬 Current smoker", "current")
]

# Dizziness Frequency Options
DIZZINESS_OPTIONS = [
    ("✅ Never", "never"),
    ("🔸 Rarely", "rarely"),
    ("🔶 Sometimes", "sometimes"),
    ("🔴 Often", "often")
]

# Therapy Frequency Options
THERAPY_FREQUENCY_OPTIONS = [
    ("❌ Never", "never"),
    ("📅 In the past", "past"),
    ("📆 Currently (monthly)", "current_monthly"),
    ("📋 Currently (weekly)", "current_weekly")
]

# Medication Adherence Options
MEDICATION_ADHERENCE_OPTIONS = [
    ("✅ Full adherence", "full"),
    ("⚠️ Partial adherence", "partial"),
    ("❌ Not taking medication", "none")
]

# Alcohol Intake Range (0-19 drinks per week)
ALCOHOL_INTAKE_RANGE = list(range(0, 20))

# Caffeine Intake Range (0-15 cups per day)
CAFFEINE_INTAKE_RANGE = list(range(0, 16))

# Sleep Hours Range (0-16 hours)
SLEEP_HOURS_RANGE = [float(x) / 2 for x in range(0, 33)]  # 0, 0.5, 1, ..., 16

# Heart Rate Range (40-200 bpm)
HEART_RATE_RANGE = (40, 200)

# Breathing Rate Range (8-30 breaths per minute)
BREATHING_RATE_RANGE = (8, 30)

# Age Range (13-120)
AGE_RANGE = (13, 120)

# Common Occupations
COMMON_OCCUPATIONS = [
    "Student",
    "Office Worker",
    "Healthcare",
    "Education",
    "Technology",
    "Retail/Sales",
    "Service Industry",
    "Self-employed",
    "Unemployed",
    "Retired",
    "Other"
]

# Life Events Examples
LIFE_EVENTS_EXAMPLES = [
    "Job change",
    "Relationship change",
    "Moving",
    "Loss of loved one",
    "Financial stress",
    "Health issues",
    "Family issues",
    "None significant"
]

# Anxiety Advice Categories
ADVICE_CATEGORIES = {
    "low": {
        "range": (1, 3),
        "category": "general",
        "icon": "💚"
    },
    "moderate": {
        "range": (4, 6),
        "category": "moderate",
        "icon": "💛"
    },
    "high": {
        "range": (7, 10),
        "category": "high_alert",
        "icon": "❤️"
    }
}

# Professional Help Warning
PROFESSIONAL_HELP_WARNING = """
⚠️ **Important Notice**

Your reported anxiety level is high. We strongly recommend:

🏥 **Consider booking an appointment with a mental health professional.**

If you're in crisis, please contact:
• National Suicide Prevention Lifeline: 988 (US)
• Crisis Text Line: Text HOME to 741741
• International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/

Remember: Seeking help is a sign of strength, not weakness.
"""

# Placeholder Advice Messages
PLACEHOLDER_ADVICE = {
    "low": [
        "🌟 Great job maintaining your mental health! Keep up your healthy habits.",
        "✨ Your anxiety levels are well-managed. Continue your self-care routine!",
        "🎯 You're doing well! Consider sharing your strategies with others."
    ],
    "moderate": [
        "💪 Try deep breathing exercises: inhale for 4 seconds, hold for 4, exhale for 4.",
        "🧘 Consider a short meditation session to help center yourself.",
        "🚶 A brief walk outside can help reduce stress and anxiety.",
        "📝 Journaling your thoughts might help process your feelings.",
        "💤 Ensure you're getting adequate sleep - it's crucial for mental health."
    ],
    "high": [
        "🆘 Your anxiety is elevated. Please consider reaching out to a professional.",
        "🏥 Speaking with a therapist can provide valuable coping strategies.",
        "📞 Don't hesitate to call a mental health hotline if you need immediate support.",
        "💊 If you're on medication, ensure you're taking it as prescribed.",
        "🤝 Reach out to a trusted friend or family member for support."
    ]
}

# Emojis
EMOJI = {
    "check": "✅",
    "cross": "❌",
    "warning": "⚠️",
    "info": "ℹ️",
    "star": "⭐",
    "heart": "❤️",
    "brain": "🧠",
    "chart": "📊",
    "calendar": "📅",
    "settings": "⚙️",
    "user": "👤",
    "admin": "👑",
    "back": "◀️",
    "forward": "▶️",
    "home": "🏠",
    "help": "❓",
    "save": "💾",
    "delete": "🗑️",
    "edit": "✏️",
    "download": "📥",
    "upload": "📤",
    "bell": "🔔",
    "mute": "🔕",
    "lock": "🔒",
    "unlock": "🔓",
    "thumbs_up": "👍",
    "thumbs_down": "👎",
    "speech": "💬",
    "rocket": "🚀",
    "fire": "🔥",
    "sparkles": "✨",
    "wave": "👋",
    "pray": "🙏",
    "muscle": "💪",
    "sleep": "😴",
    "coffee": "☕",
    "wine": "🍷",
    "pill": "💊",
    "hospital": "🏥",
    "doc": "📄",
    "folder": "📁",
    "clock": "🕐",
    "hourglass": "⏳"
}

# Messages
MESSAGES = {
    "welcome": """
🧠 **Welcome to Mental Health Bot!**

I'm here to help you track your mental health and well-being.

Here's what I can do:
• 📊 Track your daily mood and anxiety levels
• 📈 Generate personalized statistics and charts
• 💡 Provide helpful advice based on your data
• 🔔 Send weekly reminders for check-ins

Let's start by getting to know you better!
""",
    
    "onboarding_intro": """
📋 **Let's Set Up Your Profile**

I'll ask you a few questions about yourself to personalize your experience.
This will take about 5-10 minutes.

Your data is private and secure. 🔒

Ready to begin?
""",
    
    "onboarding_complete": """
🎉 **Profile Complete!**

Thank you for setting up your profile. You're all set to start tracking your mental health!

**What's Next?**
• Use /checkin for daily check-ins
• Use /stats to view your statistics
• Use /settings to manage your profile
• Use /help for more options

Take care of yourself! 💚
""",
    
    "daily_check_intro": """
📋 **Daily Check-in**

Let's see how you're doing today!
This quick check-in takes about 2-3 minutes.

💡 *Tip: For the highest accuracy, we recommend completing all questions.*
""",
    
    "extended_form_prompt": """
📝 **Extended Questions**

Would you like to answer a few more questions for a more accurate assessment?

These additional questions help us provide better insights and advice.
""",
    
    "weekly_check_intro": """
📊 **Weekly Assessment**

Time for your weekly mental health check-in!
Let's review how your week went.

This will take about 5 minutes.
""",
    
    "feedback_prompt": """
💭 **Your Feedback Matters!**

How was the prediction and advice you received?
Your feedback helps us improve!
""",
    
    "settings_menu": """
⚙️ **Settings**

What would you like to do?
""",
    
    "admin_welcome": """
👑 **Admin Panel**

Welcome to the admin dashboard!
Here you can view statistics and manage users.
""",
    
    "help_message": """
❓ **Help & Commands**

**Basic Commands:**
• /start - Start the bot
• /help - Show this help message
• /checkin - Daily check-in
• /weekly - Weekly assessment
• /stats - View your statistics
• /history - View your history
• /settings - Manage your profile

**Tips:**
• Complete daily check-ins for better tracking
• The more data you provide, the better insights you'll get
• All your data is private and secure

Need more help? Contact support.
""",
    
    "cancel_message": """
❌ **Action Cancelled**

You can start over anytime using the menu.
""",
    
    "error_message": """
⚠️ **Oops! Something went wrong.**

Please try again or contact support if the issue persists.
""",
    
    "session_timeout": """
⏰ **Session Timeout**

Your session has expired due to inactivity.
Please start over with /start or /checkin.
"""
}

# Admin Messages
ADMIN_MESSAGES = {
    "stats_header": """
📊 **Admin Dashboard**

**Overall Statistics:**
""",
    
    "user_list_header": """
👥 **User List**

Showing {start}-{end} of {total} users:
""",
    
    "export_success": """
✅ **Export Complete**

Data has been exported successfully.
""",
    
    "no_permission": """
🚫 **Access Denied**

You don't have permission to access this feature.
"""
}
