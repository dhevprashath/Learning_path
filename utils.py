import os
import io
import smtplib
import ssl
from datetime import datetime
from typing import Optional, Tuple, List, Dict
import json

from email.message import EmailMessage

from dotenv import load_dotenv
from email_validator import validate_email, EmailNotValidError
from fpdf import FPDF
import google.generativeai as genai
from youtubesearchpython import PlaylistsSearch, VideosSearch


def load_environment() -> None:
    """Load environment variables from .env file."""
    load_dotenv()


def validate_email_address(email: str) -> bool:
    """Validate email address format."""
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False


def ensure_output_dir() -> str:
    """Ensure output directory exists and return its path."""
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def search_youtube_playlist(query: str) -> Optional[str]:
    """Search for YouTube playlists and return the first result URL."""
    try:
        search = PlaylistsSearch(query, limit=1)
        results = search.result()
        if results and "result" in results and results["result"]:
            return results["result"][0]["link"]
        return None
    except Exception as e:
        print(f"YouTube search failed: {e}")
        return None


def search_youtube_videos(query: str, max_results: int = 10) -> List[Dict]:
    """Search for YouTube videos and return a list of video information."""
    try:
        search = VideosSearch(query, limit=max_results)
        results = search.result()
        videos = []
        
        if results and "result" in results:
            for video in results["result"]:
                video_info = {
                    "title": video.get("title", ""),
                    "url": video.get("link", ""),
                    "duration": video.get("duration", ""),
                    "views": video.get("viewCount", {}).get("text", ""),
                    "channel": video.get("channel", {}).get("name", ""),
                    "description": video.get("descriptionSnippet", [{}])[0].get("text", "")[:200] + "..." if video.get("descriptionSnippet") else ""
                }
                videos.append(video_info)
        
        return videos
    except Exception as e:
        print(f"YouTube video search failed: {e}")
        return []


def create_learning_playlist(topic: str, background: str, commitment: str) -> Dict:
    """Create a structured learning playlist with video recommendations."""
    # Generate search queries based on topic and background
    if "beginner" in background.lower() or "absolute" in background.lower():
        difficulty = "beginner"
        search_queries = [
            f"{topic} tutorial for beginners",
            f"{topic} basics explained",
            f"{topic} introduction course",
            f"{topic} fundamentals"
        ]
    elif "intermediate" in background.lower():
        difficulty = "intermediate"
        search_queries = [
            f"{topic} intermediate tutorial",
            f"{topic} advanced concepts",
            f"{topic} practical examples",
            f"{topic} real world applications"
        ]
    else:
        difficulty = "advanced"
        search_queries = [
            f"{topic} advanced tutorial",
            f"{topic} expert level",
            f"{topic} advanced concepts",
            f"{topic} professional development"
        ]
    
    # Search for videos using different queries
    all_videos = []
    for query in search_queries:
        videos = search_youtube_videos(query, max_results=3)
        all_videos.extend(videos)
    
    # Remove duplicates and limit results
    unique_videos = []
    seen_urls = set()
    for video in all_videos:
        if video["url"] not in seen_urls and len(unique_videos) < 15:
            unique_videos.append(video)
            seen_urls.add(video["url"])
    
    # Organize videos by learning phase
    playlist_structure = {
        "topic": topic,
        "difficulty": difficulty,
        "background": background,
        "commitment": commitment,
        "total_videos": len(unique_videos),
        "estimated_hours": len(unique_videos) * 0.5,  # Rough estimate: 30 min per video
        "phases": {
            "phase_1": {
                "name": "Foundation",
                "description": "Build basic understanding and concepts",
                "videos": unique_videos[:5] if len(unique_videos) >= 5 else unique_videos
            },
            "phase_2": {
                "name": "Core Learning",
                "description": "Deep dive into main concepts and practical examples",
                "videos": unique_videos[5:10] if len(unique_videos) >= 10 else unique_videos[5:] if len(unique_videos) > 5 else []
            },
            "phase_3": {
                "name": "Advanced Application",
                "description": "Advanced topics and real-world applications",
                "videos": unique_videos[10:] if len(unique_videos) > 10 else []
            }
        },
        "daily_schedule": generate_daily_schedule(unique_videos, commitment),
        "search_queries": search_queries
    }
    
    return playlist_structure


def generate_daily_schedule(videos: List[Dict], commitment: str) -> Dict:
    """Generate a daily learning schedule based on commitment level."""
    total_videos = len(videos)
    
    # Parse commitment to determine daily video count
    if "hour" in commitment.lower():
        if "1" in commitment or "one" in commitment:
            daily_videos = 1
        elif "2" in commitment or "two" in commitment:
            daily_videos = 2
        elif "3" in commitment or "three" in commitment:
            daily_videos = 3
        else:
            daily_videos = 2
    else:
        daily_videos = 2  # Default to 2 videos per day
    
    days_needed = max(1, total_videos // daily_videos)
    
    schedule = {}
    video_index = 0
    
    for day in range(1, days_needed + 1):
        day_videos = []
        for _ in range(daily_videos):
            if video_index < total_videos:
                day_videos.append({
                    "title": videos[video_index]["title"],
                    "url": videos[video_index]["url"],
                    "duration": videos[video_index]["duration"]
                })
                video_index += 1
        
        schedule[f"day_{day}"] = {
            "videos": day_videos,
            "estimated_time": len(day_videos) * 0.5,  # 30 min per video
            "focus": f"Complete {len(day_videos)} video(s) from the playlist"
        }
    
    return schedule


def build_ai_client() -> Optional[genai.GenerativeModel]:
    """Build Gemini client if API key is available."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-pro')


def generate_learning_notes(topic: str, background: str, commitment: str, playlist_data: Dict = None) -> str:
    """Generate learning notes using AI or fallback content."""
    client = build_ai_client()
    
    if client:
        try:
            base_context = f"""
            Topic: {topic}
            Background: {background}
            Commitment: {commitment}
            
            Generate a comprehensive learning path with:
            1. Prerequisites
            2. Learning objectives
            3. Step-by-step curriculum
            4. Recommended resources
            5. Practice exercises
            6. Timeline estimates
            """
            
            response = client.generate_content(base_context)
            return response.text
        except Exception as e:
            print(f"AI generation failed: {e}")
    
    # Fallback content
    notes = f"""
LEARNING PATH: {topic.upper()}

PREREQUISITES:
- Basic computer literacy
- Willingness to learn and practice

LEARNING OBJECTIVES:
- Understand fundamental concepts
- Build practical skills
- Complete hands-on projects
- Gain confidence in the subject

CURRICULUM:
Week 1-2: Fundamentals
- Introduction to {topic}
- Basic concepts and terminology
- Setting up development environment

Week 3-4: Core Concepts
- Key principles and methods
- Basic syntax and structure
- Simple examples and exercises

Week 5-6: Practical Application
- Building small projects
- Problem-solving exercises
- Best practices and tips

Week 7-8: Advanced Topics
- Complex concepts
- Real-world applications
- Next steps and resources

RECOMMENDED RESOURCES:
- Official documentation
- Online tutorials and courses
- Practice platforms
- Community forums

PRACTICE EXERCISES:
- Daily coding challenges
- Mini-projects
- Code reviews
- Pair programming

TIMELINE:
- Total: 8 weeks
- 5-10 hours per week
- Adjust based on your schedule

TIPS FOR SUCCESS:
- Practice regularly
- Build projects
- Join communities
- Stay consistent
- Don't rush - quality over speed

Your background: {background}
Your commitment: {commitment}

Remember: Learning is a journey, not a destination. Stay patient and persistent!
"""
    
    # Add playlist information if available
    if playlist_data:
        notes += f"""

🎥 DAILY YOUTUBE LEARNING PLAYLIST

Topic: {playlist_data['topic']}
Difficulty Level: {playlist_data['difficulty'].title()}
Total Videos: {playlist_data['total_videos']}
Estimated Total Time: {playlist_data['estimated_hours']:.1f} hours

📚 LEARNING PHASES:

Phase 1: {playlist_data['phases']['phase_1']['name']}
{playlist_data['phases']['phase_1']['description']}
Videos: {len(playlist_data['phases']['phase_1']['videos'])} videos

Phase 2: {playlist_data['phases']['phase_2']['name']}
{playlist_data['phases']['phase_2']['description']}
Videos: {len(playlist_data['phases']['phase_2']['videos'])} videos

Phase 3: {playlist_data['phases']['phase_3']['name']}
{playlist_data['phases']['phase_3']['description']}
Videos: {len(playlist_data['phases']['phase_3']['videos'])} videos

📅 DAILY SCHEDULE:
"""
        
        for day_key, day_data in playlist_data['daily_schedule'].items():
            notes += f"\n{day_key.replace('_', ' ').title()}:"
            notes += f"\n- Focus: {day_data['focus']}"
            notes += f"\n- Estimated Time: {day_data['estimated_time']:.1f} hours"
            notes += f"\n- Videos:"
            for video in day_data['videos']:
                notes += f"\n  • {video['title']} ({video['duration']})"
                notes += f"\n    Link: {video['url']}"
            notes += "\n"
        
        notes += f"""
🎯 DAILY LEARNING TIPS:
- Watch videos at your own pace
- Take notes while watching
- Practice concepts after each video
- Review previous day's content before starting new videos
- Stay consistent with your daily schedule

🔗 PLAYLIST SEARCH QUERIES USED:
{', '.join(playlist_data['search_queries'])}
"""
    
    return notes


def create_pdf_from_text(title: str, body_text: str, output_path: str) -> None:
    """Create a PDF from text content with proper formatting."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", style="B", size=18)
    pdf.multi_cell(0, 10, title)
    pdf.ln(4)

    # Body
    pdf.set_font("Helvetica", size=12)
    line_height = 7
    page_width = pdf.w - pdf.l_margin - pdf.r_margin

    def _split_token_to_fit(token: str, font_size: float, available_width: float) -> List[str]:
        """Split a long token into chunks that fit the available width."""
        pdf.set_font("Helvetica", size=font_size)
        chunks = []
        current_chunk = ""
        for char in token:
            if pdf.get_string_width(current_chunk + char) < available_width:
                current_chunk += char
            else:
                chunks.append(current_chunk)
                current_chunk = char
                
        if current_chunk:
            chunks.append(current_chunk)
        return chunks

    def _render_wrapped_text(text: str, font_size: float, line_height: float, available_width: float):
        """Render text with proper word wrapping."""
        pdf.set_font("Helvetica", size=font_size)
        words = text.split(' ')
        current_line = []
        
        for word in words:
            # Handle very long words that exceed line width
            if pdf.get_string_width(word) > available_width:
                if current_line:  # Render what's accumulated before handling the long word
                    pdf.multi_cell(available_width, line_height, ' '.join(current_line))
                    pdf.set_x(pdf.l_margin)
                    current_line = []
                # Split the long word and render its chunks
                chunks = _split_token_to_fit(word, font_size, available_width)
                for chunk in chunks:
                    pdf.multi_cell(available_width, line_height, chunk)
                    pdf.set_x(pdf.l_margin)
            else:
                test_line = ' '.join(current_line + [word])
                if pdf.get_string_width(test_line) < available_width:
                    current_line.append(word)
                else:
                    pdf.multi_cell(available_width, line_height, ' '.join(current_line))
                    pdf.set_x(pdf.l_margin)
                    current_line = [word]
        
        if current_line:
            pdf.multi_cell(available_width, line_height, ' '.join(current_line))
            pdf.set_x(pdf.l_margin)

    for line in body_text.splitlines():
        pdf.set_x(pdf.l_margin)  # Reset X position for each line
        if not line.strip():
            pdf.ln(4)
            continue
        
        try:
            _render_wrapped_text(line, 12, line_height, page_width)
        except Exception:
            # Fallback to smaller font for problematic lines
            try:
                _render_wrapped_text(line, 10, line_height, page_width)
            except Exception:
                # Last resort: skip problematic lines
                print(f"Warning: Could not render line: {line[:50]}...")
                continue

    pdf.output(output_path)


def build_pdf_filename(topic: str) -> Tuple[str, str]:
    """Build PDF filename and full path."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"learning_path_{topic.lower().replace(' ', '_')}_{timestamp}.pdf"
    output_dir = ensure_output_dir()
    full_path = os.path.join(output_dir, filename)
    return filename, full_path


def get_missing_smtp_env_keys() -> List[str]:
    """Get list of missing required SMTP environment variables."""
    required_keys = ["EMAIL_FROM", "SMTP_HOST", "SMTP_USERNAME", "SMTP_PASSWORD"]
    missing = [key for key in required_keys if not os.getenv(key)]
    return missing


def send_email_with_attachment(
    to_address: str,
    subject: str,
    body_text: str,
    attachment_bytes: bytes,
    attachment_filename: str,
) -> bool:
    """Send email via SMTP with an attached PDF. Returns True on success."""
    email_from = os.getenv("EMAIL_FROM")
    email_from_name = os.getenv("EMAIL_FROM_NAME", "Learning Path Bot")
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_secure_mode = os.getenv("SMTP_SECURE", "starttls").lower()
    smtp_timeout = int(os.getenv("SMTP_TIMEOUT", "30"))
    smtp_debug = int(os.getenv("SMTP_DEBUG", "0"))

    missing_keys = get_missing_smtp_env_keys()
    if missing_keys:
        if smtp_debug:
            print(f"Missing SMTP environment variables: {', '.join(missing_keys)}")
        return False

    msg = EmailMessage()
    msg["From"] = f"{email_from_name} <{email_from}>"
    msg["To"] = to_address
    msg["Subject"] = subject
    msg.set_content(body_text)

    msg.add_attachment(
        attachment_bytes,
        maintype="application",
        subtype="pdf",
        filename=attachment_filename,
    )

    try:
        if smtp_secure_mode == "ssl":
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=smtp_timeout, context=context) as server:
                if smtp_debug:
                    server.set_debuglevel(smtp_debug)
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
        else:  # default to starttls or none
            with smtplib.SMTP(smtp_host, smtp_port, timeout=smtp_timeout) as server:
                if smtp_debug:
                    server.set_debuglevel(smtp_debug)
                if smtp_secure_mode == "starttls":
                    context = ssl.create_default_context()
                    server.starttls(context=context)
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
        return True
    except Exception as e:
        if smtp_debug:
            print(f"Email send failed: {e}")
        return False


