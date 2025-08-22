# 🎓 Learning Path Generator

A powerful AI-driven learning path generator that creates personalized study plans with **daily YouTube playlists** and sends comprehensive PDF notes via email.

## ✨ Features

- **🎯 Personalized Learning Paths**: AI-generated study plans based on your background and commitment level
- **🎥 Daily YouTube Playlists**: Curated video recommendations organized by learning phases
- **📅 Daily Learning Schedule**: Structured daily video assignments with time estimates
- **📧 Email Delivery**: Automatic PDF delivery with embedded video links
- **📚 Comprehensive Content**: Prerequisites, objectives, curriculum, and practice exercises
- **🔍 Smart Video Search**: Intelligent video discovery based on topic and skill level

## 🚀 How It Works

1. **Input Your Learning Goal**: Tell us what you want to learn (e.g., Python, Machine Learning, Web Development)
2. **Personalize Your Profile**: Share your background and time commitment
3. **AI-Generated Content**: Get a comprehensive learning path with AI-powered insights
4. **Daily Video Playlist**: Receive a curated list of YouTube videos organized by learning phases
5. **PDF Delivery**: Get everything delivered to your email with a beautiful PDF attachment
6. **Follow Daily Schedule**: Use the included daily video schedule to stay on track

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Steps

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd learning_path
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   
   # On Windows
   .venv\Scripts\activate
   
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Copy `env_sample.txt` to `.env` and fill in your credentials:
   ```bash
   cp env_sample.txt .env
   ```
   
   Edit `.env` with your actual values:
   ```env
   # Google Gemini API Configuration
   GEMINI_API_KEY=your_gemini_api_key_here
   
   # Email Configuration
   EMAIL_FROM=your_email@gmail.com
   EMAIL_FROM_NAME=Learning Path Bot
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_SECURE=starttls
   SMTP_USERNAME=your_email@gmail.com
   SMTP_PASSWORD=your_app_password_here
   SMTP_TIMEOUT=30
   SMTP_DEBUG=0
   ```

## 🔑 Getting API Keys

### Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key
5. Paste it into your `.env` file as `GEMINI_API_KEY`

### Gmail App Password (for email functionality)
1. Enable 2-Factor Authentication on your Google account
2. Go to [Google Account Security](https://myaccount.google.com/security)
3. Generate an App Password for "Mail"
4. Use this password in your `.env` file (not your regular Gmail password)

## 🎯 Usage

### Basic Usage
```bash
python app.py
```

### Interactive Flow
1. **Enter your learning topic** (e.g., "Python", "Machine Learning", "Web Development")
2. **Provide your email** for PDF delivery
3. **Answer background questions**:
   - Current knowledge level (beginner, intermediate, advanced)
   - Time commitment and learning preferences
4. **Get your personalized learning path** with daily YouTube playlist!

### Example Session
```
🎓 Learning Path Generator
Generate personalized learning paths with AI-powered content and daily YouTube playlists!

What do you want to learn? Python
Where should we email the PDF? (leave blank to skip) student@example.com

Let's personalize your learning path:
What is your current background with this topic (e.g., absolute beginner, some basics, intermediate)? absolute beginner
How many hours per week can you realistically commit and what learning style do you prefer (reading, videos, hands-on)? 2 hours per week, prefer videos

🎥 Creating your personalized YouTube learning playlist...
✅ Successfully created playlist with 12 videos!

🎥 Learning Playlist: Python
┌─────────────┬─────────────────────────────┬─────────┬─────────────────────┐
│ Phase       │ Description                 │ Videos  │ Focus               │
├─────────────┼─────────────────────────────┼─────────┼─────────────────────┤
│ Foundation  │ Build basic understanding  │ 5       │ Complete 5 video(s) │
│ Core        │ Deep dive into main        │ 4       │ Complete 4 video(s) │
│ Advanced    │ Advanced topics and        │ 3       │ Complete 3 video(s) │
└─────────────┴─────────────────────────────┴─────────┴─────────────────────┘

📅 Daily Learning Schedule:
Total estimated time: 6.0 hours
Videos per day: 2

📚 Generating your personalized learning path...
📄 Creating PDF...
✅ PDF created successfully: learning_path_python_20241201_143022.pdf
📧 Sending email...
✅ Email sent successfully to student@example.com

🎉 Congratulations! Your learning path is ready!

📚 Topic: Python
📄 PDF: learning_path_python_20241201_143022.pdf
🎥 Videos: 12 curated videos
⏱️  Estimated Time: 6.0 hours

📧 Check your email at student@example.com for the PDF attachment with your daily schedule!
💾 PDF also saved locally at: output/learning_path_python_20241201_143022.pdf

🎯 Next Steps:
1. Open the PDF and review your learning path
2. Start with Day 1 of your video playlist
3. Follow the daily schedule consistently
4. Practice what you learn each day
```

## 📁 Project Structure

```
learning_path/
├── app.py              # Main application entry point
├── utils.py            # Core functionality and utilities
├── prompt.py           # User interaction prompts
├── requirements.txt    # Python dependencies
├── env_sample.txt      # Environment variables template
├── .env                # Your environment variables (create this)
├── output/             # Generated PDFs
└── README.md           # This file
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GEMINI_API_KEY` | Your Google Gemini API key | - | Yes |
| `EMAIL_FROM` | Sender email address | - | Yes |
| `EMAIL_FROM_NAME` | Sender name | Learning Path Bot | No |
| `SMTP_HOST` | SMTP server hostname | - | Yes |
| `SMTP_PORT` | SMTP server port | 587 | No |
| `SMTP_SECURE` | Security mode (starttls/ssl/none) | starttls | No |
| `SMTP_USERNAME` | SMTP username | - | Yes |
| `SMTP_PASSWORD` | SMTP password/app password | - | Yes |
| `SMTP_TIMEOUT` | Connection timeout (seconds) | 30 | No |
| `SMTP_DEBUG` | Enable SMTP debugging | 0 | No |

### SMTP Server Examples

#### Gmail
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_SECURE=starttls
```

#### Outlook/Hotmail
```env
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_SECURE=starttls
```

#### Yahoo
```env
SMTP_HOST=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_SECURE=starttls
```

## 🎥 YouTube Playlist Features

### Smart Video Discovery
- **Beginner Level**: Focuses on fundamentals, basics, and introduction videos
- **Intermediate Level**: Emphasizes practical examples and real-world applications
- **Advanced Level**: Targets expert-level content and professional development

### Learning Phases
1. **Foundation**: Basic concepts and terminology
2. **Core Learning**: Main concepts and practical examples
3. **Advanced Application**: Complex topics and real-world applications

### Daily Schedule
- Automatically calculates optimal daily video count based on your commitment
- Provides estimated time for each day's learning session
- Includes direct links to all recommended videos

## 📧 Email Features

### Rich Email Content
- Personalized greeting with your learning topic
- Summary of your learning profile
- Playlist statistics and daily schedule overview
- Pro tips for effective learning
- Professional PDF attachment with full learning path

### PDF Content
- Complete learning path with prerequisites and objectives
- Step-by-step curriculum with timeline estimates
- Daily video schedule with direct links
- Practice exercises and success tips
- Organized by learning phases

## 🚨 Troubleshooting

### Common Issues

1. **"Missing SMTP environment variables"**
   - Ensure you've copied `env_sample.txt` to `.env`
   - Fill in all required SMTP credentials
   - Check that your `.env` file is in the project root

2. **"Email send failed"**
   - Verify your SMTP credentials
   - For Gmail, ensure you're using an App Password, not your regular password
   - Check that 2FA is enabled on your Google account
   - Set `SMTP_DEBUG=1` in your `.env` for detailed error messages

3. **"AI generation failed"**
   - Verify your Google Gemini API key is correct
- Check your Google AI Studio account has sufficient quota
   - Ensure you have a stable internet connection

4. **"No videos found"**
   - This usually indicates a network issue or YouTube search limitation
   - The system will continue with text-based learning path
   - Try running again later

### Debug Mode
Set `SMTP_DEBUG=1` in your `.env` file to see detailed SMTP communication logs.

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve this project!

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- Google Gemini for AI-powered content generation
- YouTube for video content discovery
- Rich library for beautiful terminal interfaces
- FPDF for PDF generation capabilities

---

**Happy Learning! 🎓✨**


