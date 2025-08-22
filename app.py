import os
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from prompt import ClarifyingQuestions, build_playlist_query
from utils import (
    build_ai_client,
    build_pdf_filename,
    create_pdf_from_text,
    ensure_output_dir,
    get_missing_smtp_env_keys,
    generate_learning_notes,
    load_environment,
    search_youtube_playlist,
    search_youtube_videos,
    create_learning_playlist,
    send_email_with_attachment,
    validate_email_address,
)

console = Console()


def configure_smtp_interactively() -> bool:
    """Prompt the user for missing SMTP settings and set them in the process env."""
    console.print("[yellow]SMTP settings are required to send email.[/yellow]")
    if not Confirm.ask("Configure SMTP now?", default=True):
        return False

    smtp_host = Prompt.ask("SMTP host (e.g., smtp.gmail.com)").strip()
    smtp_port = Prompt.ask("SMTP port (587 for STARTTLS, 465 for SSL)", default="587").strip()
    smtp_secure = Prompt.ask("SMTP security (starttls/ssl/none)", default="starttls").strip().lower()
    smtp_username = Prompt.ask("SMTP username (usually your email)").strip()
    smtp_password = Prompt.ask("SMTP password/app password", password=True).strip()
    email_from = Prompt.ask("From email address", default=smtp_username).strip()
    email_from_name = Prompt.ask("From name", default="Learning Path Bot").strip()

    os.environ["SMTP_HOST"] = smtp_host
    os.environ["SMTP_PORT"] = smtp_port
    os.environ["SMTP_SECURE"] = smtp_secure
    os.environ["SMTP_USERNAME"] = smtp_username
    os.environ["SMTP_PASSWORD"] = smtp_password
    os.environ["EMAIL_FROM"] = email_from
    os.environ["EMAIL_FROM_NAME"] = email_from_name
    os.environ.setdefault("SMTP_TIMEOUT", "30")

    if Confirm.ask("Save these settings to .env for next time?", default=False):
        try:
            lines = [
                f"EMAIL_FROM={email_from}\n",
                f"EMAIL_FROM_NAME={email_from_name}\n",
                f"SMTP_HOST={smtp_host}\n",
                f"SMTP_PORT={smtp_port}\n",
                f"SMTP_USERNAME={smtp_username}\n",
                f"SMTP_PASSWORD={smtp_password}\n",
                f"SMTP_SECURE={smtp_secure}\n",
                f"SMTP_TIMEOUT=30\n",
            ]
            with open(".env", "a", encoding="utf-8") as f:
                f.write("\n" + "".join(lines))
            console.print("[green].env updated.[/green]")
        except Exception as exc:
            console.print(f"[yellow]Could not write .env: {exc}[/yellow]")
    return True


def display_playlist_summary(playlist_data: dict) -> None:
    """Display a summary of the created playlist."""
    table = Table(title=f"🎥 Learning Playlist: {playlist_data['topic']}")
    table.add_column("Phase", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")
    table.add_column("Videos", style="green", justify="center")
    table.add_column("Focus", style="yellow")
    
    for phase_key, phase_data in playlist_data['phases'].items():
        if phase_data['videos']:
            table.add_row(
                phase_data['name'],
                phase_data['description'],
                str(len(phase_data['videos'])),
                f"Complete {len(phase_data['videos'])} video(s)"
            )
    
    console.print(table)
    
    # Display daily schedule
    console.print(f"\n📅 [bold]Daily Learning Schedule:[/bold]")
    console.print(f"Total estimated time: [green]{playlist_data['estimated_hours']:.1f} hours[/green]")
    console.print(f"Videos per day: [green]{len(playlist_data['daily_schedule']['day_1']['videos']) if playlist_data['daily_schedule'] else 0}[/green]")
    
    for day_key, day_data in list(playlist_data['daily_schedule'].items())[:3]:  # Show first 3 days
        console.print(f"\n[bold]{day_key.replace('_', ' ').title()}:[/bold]")
        for video in day_data['videos']:
            console.print(f"  • [link={video['url']}]{video['title']}[/link] ({video['duration']})")


def main() -> None:
    """Main application flow."""
    load_environment()

    console.print(Panel.fit(
        "[bold cyan]🎓 Learning Path Generator[/bold cyan]\n"
        "Generate personalized learning paths with AI-powered content and daily YouTube playlists!",
        border_style="cyan"
    ))

    # Get user input
    topic = Prompt.ask("What do you want to learn?", default="Python")
    email = Prompt.ask("Where should we email the PDF? (leave blank to skip)", default="")
    
    if email and not validate_email_address(email):
        console.print("[red]Invalid email address. Email step will be skipped.[/red]")
        email = ""

    # Ask clarifying questions
    qs = ClarifyingQuestions()
    console.print(f"\n[bold]Let's personalize your learning path:[/bold]")
    answer_one = Prompt.ask(qs.question_one)
    answer_two = Prompt.ask(qs.question_two)

    # Create comprehensive learning playlist
    console.print(f"\n[bold]🎥 Creating your personalized YouTube learning playlist...[/bold]")
    playlist_data = create_learning_playlist(topic, answer_one, answer_two)
    
    if playlist_data['total_videos'] > 0:
        console.print(f"[green]✅ Successfully created playlist with {playlist_data['total_videos']} videos![/green]")
        display_playlist_summary(playlist_data)
    else:
        console.print("[yellow]⚠️  No videos found. Continuing without video resources.[/yellow]")
        playlist_data = None

    # Generate learning notes with playlist integration
    console.print(f"\n[bold]📚 Generating your personalized learning path...[/bold]")
    notes = generate_learning_notes(topic, answer_one, answer_two, playlist_data)
    
    # Create PDF
    console.print(f"\n[bold]📄 Creating PDF...[/bold]")
    pdf_name, pdf_path = build_pdf_filename(topic)
    
    try:
        create_pdf_from_text(
            title=f"Personalized Learning Path: {topic}",
            body_text=notes,
            output_path=pdf_path
        )
        console.print(f"[green]✅ PDF created successfully:[/green] {pdf_name}")
    except Exception as e:
        console.print(f"[red]❌ Failed to create PDF: {e}[/red]")
        return

    # Email step
    if email:
        console.print(f"\n[bold]📧 Sending email...[/bold]")
        missing = get_missing_smtp_env_keys()
        if missing:
            console.print(f"[yellow]⚠️  Email cannot be sent. Missing SMTP env keys: {', '.join(missing)}[/yellow]")
            if configure_smtp_interactively():
                missing = get_missing_smtp_env_keys()
        
        if not missing:
            try:
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                
                # Create enhanced email body
                email_body = f"""Hello! 👋

🎓 Attached is your personalized learning path for {topic}.

📋 Your Learning Profile:
• Background: {answer_one}
• Commitment: {answer_two}

🎥 Daily YouTube Learning Plan:
"""
                
                if playlist_data:
                    email_body += f"""• Total Videos: {playlist_data['total_videos']}
• Estimated Time: {playlist_data['estimated_hours']:.1f} hours
• Difficulty Level: {playlist_data['difficulty'].title()}
• Daily Schedule: {len(playlist_data['daily_schedule'])} days

📅 Your daily learning schedule is included in the PDF attachment.
Each day, you'll have a curated list of videos to watch and practice with.

💡 Pro Tips:
- Watch videos at your own pace
- Take notes while watching
- Practice concepts after each video
- Stay consistent with your daily schedule
"""
                else:
                    email_body += "• No YouTube playlist was found for this topic.\n"

                email_body += f"""
🚀 Ready to start your learning journey? Open the PDF and begin with Day 1!

Best of luck with your {topic} learning adventure!
- Learning Path Bot 🤖

---
Generated on: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
"""
                
                sent = send_email_with_attachment(
                    to_address=email,
                    subject=f"🎓 Your {topic} Learning Path - Daily YouTube Playlist Included!",
                    body_text=email_body,
                    attachment_bytes=pdf_bytes,
                    attachment_filename=pdf_name,
                )
                
                if sent:
                    console.print(f"[green]✅ Email sent successfully to[/green] {email}")
                else:
                    console.print("[yellow]⚠️  Email configuration missing or send failed. Set SMTP_DEBUG=1 for details. Skipped sending.[/yellow]")
            except Exception as e:
                console.print(f"[red]❌ Error sending email: {e}[/red]")
    else:
        console.print(f"\n[yellow]⚠️  No email provided. PDF saved to: {pdf_path}[/yellow]")

    # Final summary
    console.print(Panel.fit(
        f"[bold green]🎉 Congratulations! Your learning path is ready![/bold green]\n\n"
        f"📚 Topic: {topic}\n"
        f"📄 PDF: {pdf_name}\n"
        f"🎥 Videos: {playlist_data['total_videos'] if playlist_data else 0} curated videos\n"
        f"⏱️  Estimated Time: {playlist_data['estimated_hours']:.1f} hours" if playlist_data else "⏱️  Estimated Time: 8 weeks",
        border_style="green"
    ))
    
    if email:
        console.print(f"📧 Check your email at {email} for the PDF attachment with your daily schedule!")
    console.print(f"💾 PDF also saved locally at: {pdf_path}")
    
    if playlist_data:
        console.print(f"\n🎯 [bold]Next Steps:[/bold]")
        console.print(f"1. Open the PDF and review your learning path")
        console.print(f"2. Start with Day 1 of your video playlist")
        console.print(f"3. Follow the daily schedule consistently")
        console.print(f"4. Practice what you learn each day")


if __name__ == "__main__":
    main()


