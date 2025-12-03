"""
Chart generation utilities using matplotlib.
"""

import io
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np


def create_anxiety_chart(data: List[Dict[str, Any]], title: str = "Anxiety Levels Over Time") -> Optional[bytes]:
    """Create a line chart showing anxiety levels over time."""
    if not data:
        return None
    
    dates = [d['date'] for d in data]
    anxiety_levels = [d['anxiety_level'] for d in data]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot line
    ax.plot(dates, anxiety_levels, 'o-', color='#FF6B6B', linewidth=2, markersize=8)
    
    # Fill area under line
    ax.fill_between(dates, anxiety_levels, alpha=0.3, color='#FF6B6B')
    
    # Styling
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Anxiety Level (1-10)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_ylim(0, 11)
    ax.grid(True, alpha=0.3)
    
    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    plt.xticks(rotation=45)
    
    # Add threshold lines
    ax.axhline(y=3, color='green', linestyle='--', alpha=0.5, label='Low (≤3)')
    ax.axhline(y=7, color='red', linestyle='--', alpha=0.5, label='High (≥7)')
    ax.legend(loc='upper right')
    
    plt.tight_layout()
    
    # Save to bytes
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150)
    buf.seek(0)
    plt.close(fig)
    
    return buf.getvalue()


def create_stress_chart(data: List[Dict[str, Any]], title: str = "Stress Levels Over Time") -> Optional[bytes]:
    """Create a line chart showing stress levels over time."""
    if not data:
        return None
    
    dates = [d['date'] for d in data]
    stress_levels = [d['stress_level'] for d in data]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot line
    ax.plot(dates, stress_levels, 'o-', color='#4ECDC4', linewidth=2, markersize=8)
    
    # Fill area under line
    ax.fill_between(dates, stress_levels, alpha=0.3, color='#4ECDC4')
    
    # Styling
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Stress Level (1-10)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_ylim(0, 11)
    ax.grid(True, alpha=0.3)
    
    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    
    # Save to bytes
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150)
    buf.seek(0)
    plt.close(fig)
    
    return buf.getvalue()


def create_combined_chart(data: List[Dict[str, Any]], title: str = "Mental Health Overview") -> Optional[bytes]:
    """Create a combined chart with anxiety and stress levels."""
    if not data:
        return None
    
    dates = [d['date'] for d in data]
    anxiety_levels = [d.get('anxiety_level', 0) for d in data]
    stress_levels = [d.get('stress_level', 0) for d in data]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot both lines
    ax.plot(dates, anxiety_levels, 'o-', color='#FF6B6B', linewidth=2, markersize=6, label='Anxiety')
    ax.plot(dates, stress_levels, 's-', color='#4ECDC4', linewidth=2, markersize=6, label='Stress')
    
    # Styling
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Level (1-10)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_ylim(0, 11)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right')
    
    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    
    # Save to bytes
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150)
    buf.seek(0)
    plt.close(fig)
    
    return buf.getvalue()


def create_sleep_chart(data: List[Dict[str, Any]], title: str = "Sleep Hours Over Time") -> Optional[bytes]:
    """Create a bar chart showing sleep hours over time."""
    if not data:
        return None
    
    dates = [d['date'].strftime('%m/%d') for d in data]
    sleep_hours = [d['sleep_hours'] for d in data]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create bar chart
    colors = ['#95E1D3' if h >= 7 else '#F38181' for h in sleep_hours]
    bars = ax.bar(dates, sleep_hours, color=colors, edgecolor='white')
    
    # Add recommended sleep line
    ax.axhline(y=7, color='green', linestyle='--', alpha=0.7, label='Recommended (7+ hours)')
    ax.axhline(y=8, color='blue', linestyle='--', alpha=0.5, label='Optimal (8 hours)')
    
    # Styling
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Sleep Hours', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_ylim(0, 14)
    ax.legend(loc='upper right')
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save to bytes
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150)
    buf.seek(0)
    plt.close(fig)
    
    return buf.getvalue()


def create_distribution_chart(data: List[int], title: str = "Anxiety Level Distribution", 
                              xlabel: str = "Level") -> Optional[bytes]:
    """Create a histogram showing distribution of levels."""
    if not data:
        return None
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create histogram
    bins = range(1, 12)
    counts, bins, patches = ax.hist(data, bins=bins, color='#667eea', edgecolor='white', align='left')
    
    # Color bars based on severity
    for i, patch in enumerate(patches):
        if i < 3:
            patch.set_facecolor('#95E1D3')  # Green for low
        elif i < 6:
            patch.set_facecolor('#F9ED69')  # Yellow for moderate
        else:
            patch.set_facecolor('#F38181')  # Red for high
    
    # Styling
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xticks(range(1, 11))
    
    plt.tight_layout()
    
    # Save to bytes
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150)
    buf.seek(0)
    plt.close(fig)
    
    return buf.getvalue()


def create_weekly_comparison_chart(weekly_data: List[Dict[str, Any]], 
                                    title: str = "Weekly Comparison") -> Optional[bytes]:
    """Create a chart comparing weekly averages."""
    if not weekly_data:
        return None
    
    weeks = [f"Week {i+1}" for i in range(len(weekly_data))]
    anxiety_avgs = [w.get('avg_anxiety', 0) for w in weekly_data]
    stress_avgs = [w.get('avg_stress', 0) for w in weekly_data]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x = np.arange(len(weeks))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, anxiety_avgs, width, label='Anxiety', color='#FF6B6B')
    bars2 = ax.bar(x + width/2, stress_avgs, width, label='Stress', color='#4ECDC4')
    
    # Styling
    ax.set_xlabel('Week', fontsize=12)
    ax.set_ylabel('Average Level', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(weeks)
    ax.set_ylim(0, 11)
    ax.legend()
    
    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9)
    
    for bar in bars2:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    
    # Save to bytes
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150)
    buf.seek(0)
    plt.close(fig)
    
    return buf.getvalue()


def create_pie_chart(data: Dict[str, int], title: str = "Distribution") -> Optional[bytes]:
    """Create a pie chart for categorical data."""
    if not data:
        return None
    
    labels = list(data.keys())
    sizes = list(data.values())
    
    # Colors
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']
    
    fig, ax = plt.subplots(figsize=(8, 8))
    
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors[:len(labels)],
                                        autopct='%1.1f%%', startangle=90, pctdistance=0.85)
    
    # Draw center circle for donut chart
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    fig.gca().add_artist(centre_circle)
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.axis('equal')
    
    plt.tight_layout()
    
    # Save to bytes
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150)
    buf.seek(0)
    plt.close(fig)
    
    return buf.getvalue()


def create_admin_overview_chart(stats: Dict[str, Any]) -> Optional[bytes]:
    """Create an overview chart for admin dashboard."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Chart 1: User Activity
    ax1 = axes[0, 0]
    categories = ['Total Users', 'Active (7d)', 'Active (30d)']
    values = [
        stats.get('total_users', 0),
        stats.get('active_7d', 0),
        stats.get('active_30d', 0)
    ]
    colors = ['#667eea', '#4ECDC4', '#95E1D3']
    bars = ax1.bar(categories, values, color=colors)
    ax1.set_title('User Activity Overview', fontweight='bold')
    ax1.set_ylabel('Number of Users')
    for bar in bars:
        height = bar.get_height()
        ax1.annotate(f'{int(height)}', xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom')
    
    # Chart 2: Anxiety Distribution (if available)
    ax2 = axes[0, 1]
    if 'anxiety_distribution' in stats and stats['anxiety_distribution']:
        anxiety_data = stats['anxiety_distribution']
        levels = list(range(1, 11))
        counts = [anxiety_data.get(str(i), 0) for i in levels]
        colors = ['#95E1D3' if i <= 3 else '#F9ED69' if i <= 6 else '#F38181' for i in levels]
        ax2.bar(levels, counts, color=colors, edgecolor='white')
        ax2.set_xlabel('Anxiety Level')
        ax2.set_ylabel('Frequency')
        ax2.set_xticks(levels)
    ax2.set_title('Anxiety Level Distribution', fontweight='bold')
    
    # Chart 3: New Users Trend (placeholder)
    ax3 = axes[1, 0]
    if 'new_users_trend' in stats and stats['new_users_trend']:
        dates = [d['date'] for d in stats['new_users_trend']]
        counts = [d['count'] for d in stats['new_users_trend']]
        ax3.plot(dates, counts, 'o-', color='#667eea', linewidth=2)
        ax3.fill_between(dates, counts, alpha=0.3, color='#667eea')
    ax3.set_title('New Users Trend', fontweight='bold')
    ax3.set_ylabel('New Users')
    plt.sca(ax3)
    plt.xticks(rotation=45)
    
    # Chart 4: Check-in Frequency
    ax4 = axes[1, 1]
    if 'checkin_frequency' in stats and stats['checkin_frequency']:
        labels = list(stats['checkin_frequency'].keys())
        sizes = list(stats['checkin_frequency'].values())
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        ax4.pie(sizes, labels=labels, colors=colors[:len(labels)], autopct='%1.1f%%', startangle=90)
    ax4.set_title('Check-in Frequency', fontweight='bold')
    
    plt.tight_layout()
    
    # Save to bytes
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150)
    buf.seek(0)
    plt.close(fig)
    
    return buf.getvalue()
