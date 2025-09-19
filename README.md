# Automatic Applier for Indeed Jobs

⚠️ **IMPORTANT DISCLAIMER**: This bot automates job applications and may violate Indeed's Terms of Service. Use at your own risk and ensure compliance with applicable laws and website policies.

## Features

- ✅ **Comprehensive Indeed Easy Apply Support** - Handles the full multi-step workflow
- ✅ **Smart Resume Upload Detection** - Works with CV, resume, and cover letter uploads
- ✅ **Multi-Page Workflow Handling** - Contact info, questions, review, and submission pages
- ✅ **Modern Selenium with WebDriverWait** for reliability
- ✅ **Environment-based configuration** for security
- ✅ **Comprehensive logging and error handling**
- ✅ **Anti-detection measures** and human-like behavior simulation
- ✅ **Automatic ChromeDriver management**

## Indeed Easy Apply Workflow Support

The bot now properly handles Indeed's complete Easy Apply process:

### 🔄 **Workflow Steps Supported**
1. **Resume/CV Upload Pages** - Automatically detects and uploads your resume
2. **Contact Information Pages** - Auto-fills phone, address, and location data
3. **Screening Questions Pages** - Answers experience and qualification questions
4. **Review/Summary Pages** - Verifies information and handles final uploads
5. **Submission Pages** - Completes the application process

### 📄 **File Upload Features**
- **Multiple File Types**: PDF, Word documents, text files
- **Smart Detection**: Finds upload fields using 25+ selector patterns
- **CV/Resume/Cover Letter**: Handles all document upload types
- **Hidden Inputs**: Detects both visible and hidden file upload elements
- **Fallback Methods**: Uses multiple approaches if standard detection fails

### 🎯 **Question Handling**
- **Experience Questions**: Automatically answers years of experience
- **Authorization Questions**: Work eligibility and visa status
- **Personal Information**: Contact details and preferences
- **Education & Skills**: University and technical qualifications
- **Unknown Questions**: Smart fallback answers for unexpected questions

## Setup

### 1. Install Dependencies

```bash
pip install selenium python-dotenv webdriver-manager
```

### 2. Configure Environment Variables

1. Copy the example environment file:
   ```bash
   copy .env.example .env
   ```

2. Edit `.env` with your personal information:
   - **REQUIRED**: Fill in your phone number, address, city, postal code, and state
   - **OPTIONAL**: Update experience years, salary expectations, and preferences
   - **IMPORTANT**: Never commit the `.env` file to version control!

### 3. ChromeDriver Setup

The bot will automatically download and manage ChromeDriver using webdriver-manager. No manual setup required!

## Running

1. Start the application:
   ```bash
   python apply.py
   ```

2. A Chrome browser will open. Complete these steps:
   - Log into your Indeed account
   - Navigate to job search and enter your criteria
   - Close any popup dialogs (cookies, notifications, etc.)
   - Return to the terminal and press Enter

3. The bot will begin automatically applying to jobs. Monitor the console for progress logs.

4. Stop the bot anytime with `Ctrl+C`

## Configuration Options

### Experience Years
Set your years of experience for different technologies in the `.env` file:
- `PYTHON_EXPERIENCE=5`
- `JAVASCRIPT_EXPERIENCE=3`
- `JAVA_EXPERIENCE=2`
- etc.

### Application Preferences
Configure how you want to answer common questions:
- `WORK_AUTHORIZED=Yes`
- `SPONSORSHIP_NEEDED=No`
- `PREFERRED_SHIFT=Day shift`
- `DISABILITY_STATUS=Decline to answer`

### Performance Tuning
- `LOAD_DELAY=2.0` - Increase for slower internet connections
- The bot automatically limits to 10 pages maximum for safety

## Security Features

- ✅ No hardcoded personal information
- ✅ Environment variable configuration
- ✅ Sensitive data isolated from code
- ✅ Updated user agents and anti-detection

## Security & Anti-Detection Features

### 🛡️ **Advanced Security Measures**
- **Dynamic User Agent Rotation** - Uses current Chrome 129-131 versions for 2025
- **Browser Fingerprint Randomization** - Randomizes viewport, canvas, WebGL fingerprints
- **Anti-Automation Detection** - Removes webdriver properties and automation markers
- **Input Sanitization** - Prevents injection attacks through configuration validation
- **Secure Configuration** - Environment-based secrets with validation

### 🤖 **Bot Detection Avoidance**
- **Human Behavior Simulation** - Random scrolling, mouse movements, typing patterns
- **Realistic Timing** - Log-normal delay distribution instead of uniform delays
- **Rate Limiting** - Conservative 30 requests/hour to avoid triggering limits
- **Error Recovery** - Graceful handling of failures without obvious bot patterns
- **Window Management** - Proper cleanup to avoid detection

### 📊 **Enhanced Error Handling**
- **Comprehensive Logging** - Color-coded console + detailed file logging
- **Circuit Breaker Pattern** - Prevents infinite loops and cascading failures
- **Graceful Degradation** - Continues operation even when some features fail
- **Resource Management** - Proper cleanup of browser resources and windows
- **Recovery Strategies** - Multiple fallback approaches for each operation

### 🔍 **Monitoring & Statistics**
- **Real-time Progress Tracking** - Live updates on application success/failure rates
- **Performance Metrics** - Detailed timing and success rate analysis
- **Error Classification** - Categorized error reporting for troubleshooting
- **Session Persistence** - Maintains state across network interruptions

## Troubleshooting

### Common Issues

1. **ChromeDriver not found**: The bot automatically manages ChromeDriver, but ensure you have Chrome browser installed.

2. **Configuration errors**: Check that your `.env` file exists and contains required fields (PHONE_NUMBER, ADDRESS, etc.)

3. **Bot detection**: If Indeed blocks the bot:
   - Increase `LOAD_DELAY` in your `.env` file
   - Take breaks between sessions
   - Consider using different search criteria

4. **Application failures**: Check the console logs for specific error messages. The bot will skip problematic jobs and continue.

### Logs

The bot provides detailed logging:
- `INFO`: Normal operation progress
- `WARNING`: Non-critical issues (skipped jobs, missing elements)
- `ERROR`: Critical errors that may need attention

## Legal and Ethical Considerations

- ⚠️ This bot may violate Indeed's Terms of Service
- ⚠️ Automated applications may be flagged by employers
- ⚠️ Use responsibly and in compliance with applicable laws
- ⚠️ Consider the impact on other job seekers

## Changelog

### v2.0 (Security & Reliability Update)
- ✅ Moved sensitive data to environment variables
- ✅ Added modern Selenium WebDriverWait patterns
- ✅ Implemented comprehensive logging
- ✅ Added anti-detection measures
- ✅ Updated Chrome user agent to latest version
- ✅ Added automatic ChromeDriver management
- ✅ Improved error handling and recovery
- ✅ Added human-like behavior simulation
- ✅ Limited page processing for safety