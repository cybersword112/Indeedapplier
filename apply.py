from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, WebDriverException,
    ElementClickInterceptedException, StaleElementReferenceException
)
import time
import random
import logging
import os
import sys
import re
import json
from pathlib import Path
from typing import Optional, List, Dict, Tuple, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup comprehensive logging
class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors to log levels."""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)

# Configure logging with file and console handlers
def setup_logging():
    """Setup comprehensive logging system."""
    logger = logging.getLogger('indeed_bot')
    logger.setLevel(logging.DEBUG)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create logs directory
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    
    # File handler with rotation
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_handler = logging.FileHandler(
        logs_dir / f'indeed_bot_{timestamp}.log',
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logging()

@dataclass
class BotConfig:
    """Configuration class with validation."""
    load_delay: float
    resume_path: str
    phone: str
    address: str
    city: str
    postal: str
    state: str
    github: str
    linkedin: str
    university: str
    
    # Experience
    python_exp: str
    javascript_exp: str
    java_exp: str
    aws_exp: str
    django_exp: str
    analysis_exp: str
    teaching_exp: str
    programming_exp: str
    default_exp: str
    
    # Preferences
    salary: str
    work_authorized: str
    education: str
    sponsorship_needed: str
    commute_willing: str
    commute_willing_alt: str
    preferred_shift: str
    disability_status: str
    dbs_check: str
    criminal_record: str
    valid_cert: str
    gender: str
    available_hours: str
    interview_availability: str
    default_unknown_answer: str
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate_required_fields()
        self._validate_file_paths()
        self._validate_experience_values()
        self._sanitize_inputs()
    
    def _validate_required_fields(self):
        """Validate that required fields are present."""
        required_fields = ['phone', 'address', 'city', 'postal', 'state']
        missing_fields = [field for field in required_fields if not getattr(self, field)]
        
        if missing_fields:
            raise ValueError(f"Missing required configuration fields: {', '.join(missing_fields)}")
    
    def _validate_file_paths(self):
        """Validate file paths exist and are accessible."""
        resume_path = Path(self.resume_path)
        if not resume_path.exists():
            raise FileNotFoundError(f"Resume file not found: {self.resume_path}")
        
        if not resume_path.is_file():
            raise ValueError(f"Resume path is not a file: {self.resume_path}")
        
        # Check file extension
        valid_extensions = {'.pdf', '.doc', '.docx', '.txt'}
        if resume_path.suffix.lower() not in valid_extensions:
            logger.warning(f"Resume file extension {resume_path.suffix} may not be supported by Indeed")
    
    def _validate_experience_values(self):
        """Validate experience values are numeric."""
        experience_fields = [
            'python_exp', 'javascript_exp', 'java_exp', 'aws_exp', 'django_exp',
            'analysis_exp', 'teaching_exp', 'programming_exp', 'default_exp'
        ]
        
        for field in experience_fields:
            value = getattr(self, field)
            try:
                exp_years = int(value)
                if exp_years < 0 or exp_years > 50:
                    logger.warning(f"Experience value {field}={exp_years} seems unrealistic")
            except ValueError:
                raise ValueError(f"Experience field {field} must be numeric, got: {value}")
    
    def _sanitize_inputs(self):
        """Sanitize input values to prevent injection attacks."""
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '|', '`']
        
        for field_name in self.__dataclass_fields__:
            value = getattr(self, field_name)
            if isinstance(value, str):
                for char in dangerous_chars:
                    if char in value:
                        logger.warning(f"Removed dangerous character '{char}' from {field_name}")
                        value = value.replace(char, '')
                setattr(self, field_name, value)

def load_config() -> BotConfig:
    """Load and validate configuration from environment variables."""
    try:
        config = BotConfig(
            load_delay=float(os.getenv('LOAD_DELAY', '2.0')),
            resume_path=os.path.abspath(os.getenv('RESUME_PATH', 'resume.pdf')),
            phone=os.getenv('PHONE_NUMBER', ''),
            address=os.getenv('ADDRESS', ''),
            city=os.getenv('CITY', ''),
            postal=os.getenv('POSTAL_CODE', ''),
            state=os.getenv('STATE', ''),
            github=os.getenv('GITHUB_URL', ''),
            linkedin=os.getenv('LINKEDIN_URL', ''),
            university=os.getenv('UNIVERSITY', ''),
            
            # Experience
            python_exp=os.getenv('PYTHON_EXPERIENCE', '0'),
            javascript_exp=os.getenv('JAVASCRIPT_EXPERIENCE', '0'),
            java_exp=os.getenv('JAVA_EXPERIENCE', '0'),
            aws_exp=os.getenv('AWS_EXPERIENCE', '0'),
            django_exp=os.getenv('DJANGO_EXPERIENCE', '0'),
            analysis_exp=os.getenv('ANALYSIS_EXPERIENCE', '0'),
            teaching_exp=os.getenv('TEACHING_EXPERIENCE', '0'),
            programming_exp=os.getenv('PROGRAMMING_EXPERIENCE', '0'),
            default_exp=os.getenv('DEFAULT_EXPERIENCE', '0'),
            
            # Preferences
            salary=os.getenv('SALARY_EXPECTATION', ''),
            work_authorized=os.getenv('WORK_AUTHORIZED', 'Yes'),
            education=os.getenv('EDUCATION_LEVEL', 'Bachelor'),
            sponsorship_needed=os.getenv('SPONSORSHIP_NEEDED', 'No'),
            commute_willing=os.getenv('COMMUTE_WILLING', 'Yes'),
            commute_willing_alt=os.getenv('COMMUTE_WILLING_ALT', 'Yes'),
            preferred_shift=os.getenv('PREFERRED_SHIFT', 'Day shift'),
            disability_status=os.getenv('DISABILITY_STATUS', 'Decline to answer'),
            dbs_check=os.getenv('DBS_CHECK', 'Yes'),
            criminal_record=os.getenv('CRIMINAL_RECORD', 'No'),
            valid_cert=os.getenv('VALID_CERTIFICATE', 'Yes'),
            gender=os.getenv('GENDER', 'Decline to answer'),
            available_hours=os.getenv('AVAILABLE_HOURS', 'Yes'),
            interview_availability=os.getenv('INTERVIEW_AVAILABILITY', 'Flexible'),
            default_unknown_answer=os.getenv('DEFAULT_UNKNOWN_ANSWER', 'Yes'),
        )
        
        logger.info("Configuration loaded and validated successfully")
        return config
        
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        raise

class BotDetectionAvoidance:
    """Advanced bot detection avoidance techniques."""
    
    @staticmethod
    def get_random_user_agent() -> str:
        """Generate a random but realistic user agent for 2025."""
        # Current Chrome versions as of September 2025
        chrome_versions = ['129.0.0.0', '130.0.0.0', '131.0.0.0']
        webkit_versions = ['537.36', '537.37']
        
        chrome_version = random.choice(chrome_versions)
        webkit_version = random.choice(webkit_versions)
        
        return f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/{webkit_version} (KHTML, like Gecko) Chrome/{chrome_version} Safari/{webkit_version}"
    
    @staticmethod
    def add_fingerprint_randomization(options: Options) -> None:
        """Add advanced anti-fingerprinting measures."""
        # Randomize viewport size
        width = random.randint(1200, 1920)
        height = random.randint(800, 1080)
        options.add_argument(f"--window-size={width},{height}")
        
        # Randomize canvas fingerprinting
        options.add_argument("--disable-canvas-fingerprinting")
        options.add_argument("--disable-webgl-fingerprinting")
        
        # Additional anti-detection
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("--disable-ipc-flooding-protection")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Randomize language and timezone
        languages = ['en-US,en;q=0.9', 'en-GB,en;q=0.9', 'en-CA,en;q=0.9']
        options.add_argument(f"--accept-lang={random.choice(languages)}")

class HumanBehaviorSimulator:
    """Simulate human-like behavior to avoid detection."""
    
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.last_action_time = time.time()
    
    def human_delay(self, min_delay: float = 1.0, max_delay: float = 3.0) -> None:
        """Add realistic human-like delays."""
        # Ensure minimum time between actions
        time_since_last = time.time() - self.last_action_time
        if time_since_last < 0.5:
            time.sleep(0.5 - time_since_last)
        
        # Add random delay with realistic distribution (not uniform)
        delay = random.lognormvariate(
            mu=random.uniform(min_delay, max_delay) / 2,
            sigma=0.5
        )
        delay = max(min_delay, min(delay, max_delay))
        
        time.sleep(delay)
        self.last_action_time = time.time()
    
    def human_type(self, element, text: str) -> None:
        """Type text with human-like patterns."""
        element.clear()
        
        for char in text:
            element.send_keys(char)
            # Random typing speed
            typing_delay = random.uniform(0.05, 0.15)
            time.sleep(typing_delay)
        
        # Occasionally make "typos" and correct them for very human behavior
        if random.random() < 0.05 and len(text) > 3:  # 5% chance
            element.send_keys(Keys.BACKSPACE)
            time.sleep(random.uniform(0.1, 0.3))
            element.send_keys(text[-1])
    
    def random_scroll(self) -> None:
        """Perform random scrolling to mimic human reading behavior."""
        if random.random() < 0.3:  # 30% chance to scroll
            scroll_direction = random.choice(['up', 'down'])
            scroll_amount = random.randint(100, 300)
            
            if scroll_direction == 'down':
                self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            else:
                self.driver.execute_script(f"window.scrollBy(0, -{scroll_amount});")
            
            time.sleep(random.uniform(0.5, 1.5))
    
    def random_mouse_movement(self) -> None:
        """Perform random mouse movements."""
        if random.random() < 0.2:  # 20% chance
            try:
                # Get a random element to move to
                elements = self.driver.find_elements(By.TAG_NAME, "div")[:10]
                if elements:
                    target = random.choice(elements)
                    ActionChains(self.driver).move_to_element(target).perform()
                    time.sleep(random.uniform(0.1, 0.5))
            except Exception:
                pass  # Ignore errors in mouse simulation

class RateLimiter:
    """Implement rate limiting to avoid triggering anti-bot measures."""
    
    def __init__(self, max_requests: int = 50, time_window: int = 3600):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def wait_if_needed(self) -> None:
        """Wait if rate limit would be exceeded."""
        now = time.time()
        
        # Clean old requests
        self.requests = [req_time for req_time in self.requests 
                        if now - req_time < self.time_window]
        
        if len(self.requests) >= self.max_requests:
            sleep_time = self.time_window - (now - self.requests[0]) + 1
            logger.warning(f"Rate limit reached. Sleeping for {sleep_time:.1f} seconds")
            time.sleep(sleep_time)
            
        self.requests.append(now)

def setup_driver(config: BotConfig) -> webdriver.Chrome:
    """Setup Chrome driver with advanced anti-detection measures."""
    options = Options()
    
    # User agent randomization
    user_agent = BotDetectionAvoidance.get_random_user_agent()
    options.add_argument(f"user-agent={user_agent}")
    logger.info(f"Using user agent: {user_agent}")
    
    # Anti-detection measures
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Add fingerprint randomization
    BotDetectionAvoidance.add_fingerprint_randomization(options)
    
    # Performance and stability
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    
    # Memory and performance optimization
    options.add_argument("--memory-pressure-off")
    options.add_argument("--max_old_space_size=4096")
    
    try:
        # Try to use webdriver-manager for automatic ChromeDriver management
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            logger.info("ChromeDriver initialized using webdriver-manager")
        except ImportError:
            logger.warning("webdriver-manager not installed, falling back to system ChromeDriver")
            driver = webdriver.Chrome(options=options)
            logger.info("ChromeDriver initialized from system PATH")
        
        # Advanced anti-detection scripts
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
        driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
        
        # Set realistic window size
        driver.set_window_size(random.randint(1200, 1920), random.randint(800, 1080))
        
        logger.info("Browser setup completed successfully")
        return driver
        
    except Exception as e:
        logger.error(f"Failed to initialize ChromeDriver: {e}")
        logger.error("Troubleshooting steps:")
        logger.error("1. Ensure Chrome browser is installed")
        logger.error("2. Run: pip install webdriver-manager")
        logger.error("3. Check your internet connection")
        raise WebDriverException(f"Driver initialization failed: {e}")

class SafeElementHandler:
    """Safe element handling with comprehensive error recovery."""
    
    def __init__(self, driver: webdriver.Chrome, human_sim: HumanBehaviorSimulator):
        self.driver = driver
        self.human_sim = human_sim
    
    def safe_find_element(self, by: By, value: str, timeout: int = 10) -> Optional[object]:
        """Safely find element with retries and error handling."""
        for attempt in range(3):
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((by, value))
                )
                return element
            except TimeoutException:
                if attempt < 2:
                    logger.debug(f"Element not found (attempt {attempt + 1}): {by}={value}")
                    time.sleep(1)
                else:
                    logger.warning(f"Element not found after 3 attempts: {by}={value}")
                    return None
            except Exception as e:
                logger.error(f"Unexpected error finding element: {e}")
                return None
    
    def safe_click(self, element) -> bool:
        """Safely click element with multiple strategies."""
        if not element:
            return False
        
        strategies = [
            lambda: element.click(),
            lambda: self.driver.execute_script("arguments[0].click();", element),
            lambda: ActionChains(self.driver).move_to_element(element).click().perform()
        ]
        
        for i, strategy in enumerate(strategies):
            try:
                # Add human behavior simulation
                if i == 0:  # Only for regular clicks
                    self.human_sim.random_scroll()
                    self.human_sim.random_mouse_movement()
                
                strategy()
                self.human_sim.human_delay(0.5, 1.5)
                return True
                
            except (ElementClickInterceptedException, StaleElementReferenceException) as e:
                logger.debug(f"Click strategy {i + 1} failed: {e}")
                if i < len(strategies) - 1:
                    time.sleep(0.5)
                    continue
            except Exception as e:
                logger.warning(f"Click strategy {i + 1} unexpected error: {e}")
                continue
        
        logger.error("All click strategies failed")
        return False
    
    def safe_send_keys(self, element, text: str) -> bool:
        """Safely send keys with human-like typing."""
        if not element or not text:
            return False
        
        try:
            # Scroll element into view
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.5)
            
            # Use human-like typing
            self.human_sim.human_type(element, text)
            return True
            
        except Exception as e:
            logger.error(f"Failed to send keys '{text}': {e}")
            return False

def wait_for_element(driver, by, value, timeout=10):
    """Wait for element to be present and return it."""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        logger.warning(f"Timeout waiting for element: {by}={value}")
        return None

def wait_for_clickable(driver, by, value, timeout=10):
    """Wait for element to be clickable and return it."""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        return element
    except TimeoutException:
        logger.warning(f"Timeout waiting for clickable element: {by}={value}")
        return None

def human_like_delay(min_delay=1, max_delay=3):
    """Add a random delay to mimic human behavior."""
    delay = random.uniform(min_delay, max_delay)
    time.sleep(delay)

def main():
    """Main application logic with comprehensive error handling and security."""
    try:
        # Load and validate configuration
        config = load_config()
        logger.info("Starting Indeed Job Application Bot")
        
        # Initialize rate limiter and driver
        rate_limiter = RateLimiter(max_requests=30, time_window=3600)  # Conservative rate limiting
        driver = setup_driver(config)
        
        # Initialize human behavior simulator and safe element handler
        human_sim = HumanBehaviorSimulator(driver)
        element_handler = SafeElementHandler(driver, human_sim)
        
        # Application statistics
        stats = {
            'applications_attempted': 0,
            'applications_successful': 0,
            'applications_failed': 0,
            'pages_processed': 0,
            'start_time': datetime.now()
        }
        
        try:
            logger.info("Navigating to Indeed login page...")
            driver.get("https://www.indeed.com/account/login")
            
            # Wait for user to complete login
            print("\n" + "="*60)
            print("🔐 MANUAL LOGIN REQUIRED")
            print("="*60)
            print("1. Complete login to your Indeed account")
            print("2. Navigate to job search and enter your criteria")
            print("3. Close any popup dialogs (cookies, notifications, etc.)")
            print("4. Return here and press Enter to continue")
            print("="*60)
            input("\nPress Enter when ready to start automation: ")
            
            # Verify we're on a job search results page
            current_url = driver.current_url
            if "indeed.com" not in current_url or "jobs" not in current_url:
                logger.warning("Current page doesn't appear to be Indeed job results. Continuing anyway...")
            
            # Get total results with enhanced error handling
            total_results_element = element_handler.safe_find_element(
                By.CLASS_NAME, "jobsearch-JobCountAndSortPane-jobCount", timeout=10
            )
            
            if not total_results_element:
                # Try alternative selectors for job count
                alternative_selectors = [
                    "span[data-testid='searchResultsCountText']",
                    ".np-SearchResultsHeaderContainer span",
                    "[data-testid='job-count']"
                ]
                
                for selector in alternative_selectors:
                    total_results_element = element_handler.safe_find_element(
                        By.CSS_SELECTOR, selector, timeout=5
                    )
                    if total_results_element:
                        break
            
            if not total_results_element:
                logger.error("Could not find job count element. Page may have changed or no jobs found.")
                logger.info("Attempting to continue with estimated job count...")
                total_results_int = 100  # Default assumption
            else:
                try:
                    results_text = total_results_element.text
                    # Extract number from text like "1,234 jobs" or "Page 1 of 45 jobs"
                    numbers = re.findall(r'[\d,]+', results_text.replace(',', ''))
                    total_results_int = int(numbers[0]) if numbers else 100
                except (ValueError, IndexError):
                    logger.warning(f"Could not parse job count from: {results_text}")
                    total_results_int = 100
            
            logger.info(f"Found approximately {total_results_int:,} jobs to process")
            
            # Calculate pages with safety limits
            items_per_page = 15
            max_safe_pages = min(total_results_int // items_per_page, 5)  # Reduced for safety
            
            logger.info(f"Will process up to {max_safe_pages} pages ({max_safe_pages * items_per_page} jobs)")
            
            # Main processing loop
            for page_num in range(max_safe_pages):
                stats['pages_processed'] += 1
                logger.info(f"🔄 Processing page {page_num + 1} of {max_safe_pages}")
                
                # Rate limiting check
                rate_limiter.wait_if_needed()
                
                try:
                    # Wait for job results to load with multiple selectors
                    job_selectors = [
                        ".mosaic-provider-jobcards .tapItem",
                        "[data-testid='job-card']",
                        ".job_seen_beacon",
                        ".slider_container .slider_item"
                    ]
                    
                    results = []
                    for selector in job_selectors:
                        results = driver.find_elements(By.CSS_SELECTOR, selector)
                        if results:
                            logger.debug(f"Found {len(results)} jobs using selector: {selector}")
                            break
                    
                    if not results:
                        logger.warning(f"No job results found on page {page_num + 1}")
                        continue
                    
                    # Process each job with enhanced error handling
                    for job_index, job_result in enumerate(results):
                        job_number = job_index + 1
                        logger.info(f"📋 Processing job {job_number}/{len(results)} on page {page_num + 1}")
                        
                        try:
                            stats['applications_attempted'] += 1
                            
                            # Human-like behavior before clicking
                            human_sim.random_scroll()
                            human_sim.random_mouse_movement()
                            
                            # Click on job listing with safe handler
                            if not element_handler.safe_click(job_result):
                                logger.warning(f"Could not click job {job_number}, skipping")
                                continue
                            
                            human_sim.human_delay(1, 3)
                            
                            # Look for apply button with multiple strategies
                            apply_button = None
                            apply_selectors = [
                                ".ia-IndeedApplyButton",
                                "[data-testid='apply-button']",
                                "button[aria-label*='Apply']",
                                ".indeed-apply-button",
                                "a[href*='apply']"
                            ]
                            
                            for selector in apply_selectors:
                                apply_button = element_handler.safe_find_element(
                                    By.CSS_SELECTOR, selector, timeout=3
                                )
                                if apply_button:
                                    button_text = apply_button.text.lower()
                                    if any(word in button_text for word in ['apply', 'easy apply']):
                                        break
                                    apply_button = None
                            
                            if not apply_button:
                                logger.info(f"No Easy Apply button found for job {job_number}, skipping")
                                continue
                            
                            logger.info(f"✅ Found Easy Apply button for job {job_number}")
                            
                            # Click apply button
                            if not element_handler.safe_click(apply_button):
                                logger.warning(f"Could not click apply button for job {job_number}")
                                continue
                            
                            human_sim.human_delay(2, 4)
                            
                            # Handle application workflow
                            success = process_application_workflow(
                                driver, config, element_handler, human_sim, job_number
                            )
                            
                            if success:
                                stats['applications_successful'] += 1
                                logger.info(f"✅ Successfully applied to job {job_number}")
                            else:
                                stats['applications_failed'] += 1
                                logger.warning(f"❌ Failed to complete application for job {job_number}")
                            
                            # Ensure we're back on the main window
                            if len(driver.window_handles) > 1:
                                driver.close()
                                driver.switch_to.window(driver.window_handles[0])
                            
                            # Log progress periodically
                            if stats['applications_attempted'] % 5 == 0:
                                elapsed = datetime.now() - stats['start_time']
                                logger.info(f"📊 Progress: {stats['applications_attempted']} attempted, "
                                          f"{stats['applications_successful']} successful, "
                                          f"elapsed: {elapsed}")
                            
                        except Exception as job_error:
                            stats['applications_failed'] += 1
                            logger.error(f"❌ Error processing job {job_number}: {job_error}")
                            
                            # Recovery: ensure we're on the main window
                            try:
                                windows = driver.window_handles
                                if len(windows) > 1:
                                    driver.close()
                                driver.switch_to.window(windows[0])
                            except Exception:
                                pass
                            
                            continue
                    
                    # Navigate to next page if not the last page
                    if page_num < max_safe_pages - 1:
                        if not navigate_to_next_page(driver, element_handler, human_sim, page_num + 1):
                            logger.warning("Could not navigate to next page, ending pagination")
                            break
                    
                except Exception as page_error:
                    logger.error(f"❌ Error processing page {page_num + 1}: {page_error}")
                    
                    # Recovery strategy
                    try:
                        logger.info("Attempting page recovery...")
                        driver.refresh()
                        human_sim.human_delay(3, 5)
                    except Exception:
                        logger.error("Page recovery failed, stopping execution")
                        break
            
        except KeyboardInterrupt:
            logger.info("⏹️  Process interrupted by user")
        except Exception as critical_error:
            logger.error(f"💥 Critical error in main loop: {critical_error}")
        finally:
            # Final statistics and cleanup
            elapsed_time = datetime.now() - stats['start_time']
            logger.info("\n" + "="*60)
            logger.info("📊 FINAL STATISTICS")
            logger.info("="*60)
            logger.info(f"⏱️  Total runtime: {elapsed_time}")
            logger.info(f"📄 Pages processed: {stats['pages_processed']}")
            logger.info(f"🎯 Applications attempted: {stats['applications_attempted']}")
            logger.info(f"✅ Applications successful: {stats['applications_successful']}")
            logger.info(f"❌ Applications failed: {stats['applications_failed']}")
            
            if stats['applications_attempted'] > 0:
                success_rate = (stats['applications_successful'] / stats['applications_attempted']) * 100
                logger.info(f"📈 Success rate: {success_rate:.1f}%")
            
            logger.info("="*60)
            
    except Exception as startup_error:
        logger.error(f"💥 Failed to start application: {startup_error}")
        return 1
    finally:
        try:
            logger.info("🔄 Closing browser...")
            driver.quit()
        except Exception:
            pass
    
    return 0

def process_application_workflow(
    driver: webdriver.Chrome, 
    config: BotConfig, 
    element_handler: SafeElementHandler, 
    human_sim: HumanBehaviorSimulator, 
    job_number: int
) -> bool:
    """Process the complete Indeed Easy Apply workflow."""
    try:
        # Switch to application window if opened in new window/tab
        windows = driver.window_handles
        if len(windows) > 1:
            driver.switch_to.window(windows[-1])
        
        max_workflow_steps = 12  # Reasonable limit for workflow steps
        
        for step in range(max_workflow_steps):
            try:
                # Check if already applied
                if check_already_applied(driver):
                    logger.info(f"Already applied to job {job_number}")
                    return True
                
                # Detect current page type and handle accordingly
                page_info = detect_page_type(driver, element_handler)
                logger.debug(f"Step {step + 1}: {page_info['type']} page - {page_info['title']}")
                
                # Handle different page types
                if page_info['type'] == 'upload':
                    handle_upload_page(driver, config, element_handler, page_info['title'])
                elif page_info['type'] == 'contact':
                    handle_contact_page(driver, config, element_handler)
                elif page_info['type'] == 'questions':
                    handle_questions_page(driver, config, element_handler)
                elif page_info['type'] == 'review':
                    handle_review_page(driver, config, element_handler, page_info['title'])
                else:
                    # Fallback: try to handle any upload fields
                    handle_upload_page(driver, config, element_handler, page_info['title'])
                
                # Try to proceed to next step
                if proceed_to_next_step(driver, element_handler, human_sim):
                    # Check if application was submitted
                    human_sim.human_delay(1, 2)
                    if check_application_submitted(driver):
                        logger.info(f"Application submitted successfully for job {job_number}")
                        return True
                else:
                    logger.warning(f"Could not proceed from step {step + 1}")
                    break
                    
            except Exception as step_error:
                logger.error(f"Error in workflow step {step + 1}: {step_error}")
                break
        
        logger.warning(f"Workflow completed but application status unclear for job {job_number}")
        return False
        
    except Exception as workflow_error:
        logger.error(f"Critical error in application workflow: {workflow_error}")
        return False

def detect_page_type(driver: webdriver.Chrome, element_handler: SafeElementHandler) -> Dict[str, str]:
    """Detect the type of Indeed application page."""
    page_info = {'type': 'unknown', 'title': ''}
    
    # Try to get page title
    title_selectors = [
        ".ia-BasePage-heading",
        "h1", "h2", 
        ".ia-PageTitle",
        "[data-testid='page-title']"
    ]
    
    for selector in title_selectors:
        title_element = element_handler.safe_find_element(By.CSS_SELECTOR, selector, timeout=3)
        if title_element:
            page_info['title'] = title_element.text.strip()
            break
    
    title_lower = page_info['title'].lower()
    
    # Classify page type based on title and content
    if any(keyword in title_lower for keyword in ['resume', 'cv', 'upload', 'documents']):
        page_info['type'] = 'upload'
    elif any(keyword in title_lower for keyword in ['contact', 'information', 'details']):
        page_info['type'] = 'contact'
    elif any(keyword in title_lower for keyword in ['questions', 'screening', 'assessment']):
        page_info['type'] = 'questions'
    elif any(keyword in title_lower for keyword in ['review', 'summary', 'confirm']):
        page_info['type'] = 'review'
    else:
        # Check page content for classification
        if driver.find_elements(By.CSS_SELECTOR, 'input[type="file"]'):
            page_info['type'] = 'upload'
        elif driver.find_elements(By.CSS_SELECTOR, '.ia-Questions-item'):
            page_info['type'] = 'questions'
        elif driver.find_elements(By.CSS_SELECTOR, 'input[name*="phone"], input[name*="email"]'):
            page_info['type'] = 'contact'
    
    return page_info

# Additional utility functions would continue here...
# For brevity, I'll add the key remaining functions

def navigate_to_next_page(
    driver: webdriver.Chrome, 
    element_handler: SafeElementHandler, 
    human_sim: HumanBehaviorSimulator, 
    page_num: int
) -> bool:
    """Navigate to the next page of job results."""
    next_selectors = [
        "//a[@data-testid='pagination-page-next']",
        "//a[@aria-label='Next Page']",
        "//a[contains(@href, 'start=')]",
        "//span[text()='Next']/.."
    ]
    
    for selector in next_selectors:
        next_button = element_handler.safe_find_element(By.XPATH, selector, timeout=5)
        if next_button and next_button.is_enabled():
            logger.info(f"Navigating to page {page_num + 1}")
            if element_handler.safe_click(next_button):
                human_sim.human_delay(3, 6)  # Wait for page load
                return True
    
    logger.warning("No next page button found or clickable")
    return False

if __name__ == "__main__":
    sys.exit(main())

# Add missing utility functions after detect_page_type function

def check_already_applied(driver: webdriver.Chrome) -> bool:
    """Check if already applied to this job."""
    already_applied_selectors = [
        ".ia-HasApplied-bodyTop",
        "[data-testid='already-applied']",
        ".already-applied",
        "*:contains('already applied')",
        "*:contains('application submitted')"
    ]
    
    for selector in already_applied_selectors:
        try:
            if ':contains(' in selector:
                text = selector.split("'")[1]
                elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")
            else:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
            
            if elements:
                return True
        except Exception:
            continue
    
    return False

def check_application_submitted(driver: webdriver.Chrome) -> bool:
    """Check if application was successfully submitted."""
    success_indicators = [
        "application submitted",
        "application sent",
        "application complete",
        "thank you for applying",
        "your application has been sent"
    ]
    
    page_text = driver.page_source.lower()
    return any(indicator in page_text for indicator in success_indicators)

def handle_upload_page(driver: webdriver.Chrome, config: BotConfig, element_handler: SafeElementHandler, page_title: str) -> bool:
    """Handle file upload pages."""
    try:
        if not os.path.exists(config.resume_path):
            logger.warning(f"Resume file not found: {config.resume_path}")
            return False
        
        upload_selectors = [
            'input[data-testid="FileUpload-input"]',
            'input[data-testid="resume-upload"]',
            'input[type="file"]',
            '.ia-FileUpload input[type="file"]'
        ]
        
        for selector in upload_selectors:
            try:
                file_inputs = driver.find_elements(By.CSS_SELECTOR, selector)
                for file_input in file_inputs:
                    if file_input.is_enabled():
                        file_input.send_keys(config.resume_path)
                        logger.info(f"Uploaded resume: {os.path.basename(config.resume_path)}")
                        time.sleep(2)
                        return True
            except Exception as e:
                logger.debug(f"Upload attempt failed for {selector}: {e}")
                continue
        
        return False
        
    except Exception as e:
        logger.error(f"Error in upload handler: {e}")
        return False

def handle_contact_page(driver: webdriver.Chrome, config: BotConfig, element_handler: SafeElementHandler) -> bool:
    """Handle contact information pages."""
    try:
        contact_fields = [
            ('input[name*="phone"]', config.phone),
            ('input[name*="address"]', config.address),
            ('input[name*="city"]', config.city),
            ('input[name*="state"]', config.state),
            ('input[name*="zip"]', config.postal),
            ('input[name*="postal"]', config.postal),
        ]
        
        filled_count = 0
        for selector, value in contact_fields:
            if value:
                try:
                    field = driver.find_element(By.CSS_SELECTOR, selector)
                    if field.is_enabled() and not field.get_attribute('value'):
                        field.clear()
                        field.send_keys(value)
                        filled_count += 1
                        logger.info(f"Filled contact field: {selector}")
                except NoSuchElementException:
                    continue
                except Exception as e:
                    logger.debug(f"Error filling {selector}: {e}")
        
        return filled_count > 0
        
    except Exception as e:
        logger.error(f"Error handling contact page: {e}")
        return False

def handle_questions_page(driver: webdriver.Chrome, config: BotConfig, element_handler: SafeElementHandler) -> bool:
    """Handle screening questions pages."""
    try:
        questions = driver.find_elements(By.CLASS_NAME, "ia-Questions-item")
        if not questions:
            questions = driver.find_elements(By.CSS_SELECTOR, '[data-testid*="question"], .ia-Question')
        
        answered_count = 0
        for question in questions:
            try:
                question_text_elem = question.find_element(By.CSS_SELECTOR, ".css-kyg8or, label, .question-text")
                question_text = question_text_elem.text
                
                if handle_individual_question(question, question_text, config):
                    answered_count += 1
                    
            except Exception as e:
                logger.debug(f"Error processing question: {e}")
        
        return answered_count > 0
        
    except Exception as e:
        logger.error(f"Error handling questions page: {e}")
        return False

def handle_individual_question(question, question_text: str, config: BotConfig) -> bool:
    """Handle individual question with config-based answers."""
    question_lower = question_text.lower()
    
    # Text input questions
    text_mappings = {
        'python experience': config.python_exp,
        'javascript experience': config.javascript_exp,
        'java experience': config.java_exp,
        'aws experience': config.aws_exp,
        'django experience': config.django_exp,
        'programming experience': config.programming_exp,
        'phone': config.phone,
        'address': config.address,
        'city': config.city,
        'salary': config.salary,
        'experience': config.default_exp,
    }
    
    # Multiple choice questions
    choice_mappings = {
        'authorization': config.work_authorized,
        'authorized': config.work_authorized,
        'education': config.education,
        'sponsorship': config.sponsorship_needed,
        'commute': config.commute_willing,
        'shift': config.preferred_shift,
        'disability': config.disability_status,
        'criminal': config.criminal_record,
        'gender': config.gender,
    }
    
    try:
        # Handle text inputs
        for keyword, answer in text_mappings.items():
            if keyword in question_lower and answer:
                try:
                    input_field = question.find_element(By.CSS_SELECTOR, '[id^="input-q"], input[type="text"], input[type="number"]')
                    input_field.clear()
                    input_field.send_keys(answer)
                    logger.info(f"Answered text question: {keyword}")
                    return True
                except NoSuchElementException:
                    continue
        
        # Handle multiple choice
        for keyword, answer in choice_mappings.items():
            if keyword in question_lower and answer:
                try:
                    choice = question.find_element(By.XPATH, f'//*[contains(text(), "{answer}")]')
                    choice.click()
                    logger.info(f"Answered choice question: {keyword}")
                    return True
                except NoSuchElementException:
                    continue
        
        # Default handling for unknown questions
        try:
            input_field = question.find_element(By.CSS_SELECTOR, '[id^="input-q"], input[type="text"]')
            input_field.clear()
            input_field.send_keys(config.default_exp)
            logger.info("Answered unknown question with default")
            return True
        except NoSuchElementException:
            pass
        
        try:
            choice = question.find_element(By.XPATH, f'//*[contains(text(), "{config.default_unknown_answer}")]')
            choice.click()
            logger.info("Answered unknown choice question with default")
            return True
        except NoSuchElementException:
            pass
        
        return False
        
    except Exception as e:
        logger.error(f"Error handling question '{question_text}': {e}")
        return False

def handle_review_page(driver: webdriver.Chrome, config: BotConfig, element_handler: SafeElementHandler, page_title: str) -> bool:
    """Handle review/summary pages."""
    try:
        # On review pages, try to upload resume if not done yet
        return handle_upload_page(driver, config, element_handler, page_title)
    except Exception as e:
        logger.error(f"Error handling review page: {e}")
        return False

def proceed_to_next_step(driver: webdriver.Chrome, element_handler: SafeElementHandler, human_sim: HumanBehaviorSimulator) -> bool:
    """Try to proceed to the next step in the application workflow."""
    button_selectors = [
        # Submit/Complete buttons (highest priority)
        'button[data-testid="submit-application"]',
        'button[data-testid="complete-application"]',
        'button[aria-label*="Submit"]',
        '.css-njr1op',
        
        # Continue/Next buttons
        'button[data-testid="continue"]',
        'button[data-testid="next"]',
        'button[aria-label*="Continue"]',
        'button[aria-label*="Next"]',
        '.css-1gljdq7',
        '.css-10w34ze',
        
        # Generic patterns
        'input[type="submit"]',
        'button[type="submit"]',
    ]
    
    for selector in button_selectors:
        try:
            buttons = driver.find_elements(By.CSS_SELECTOR, selector)
            for button in buttons:
                if button.is_enabled() and button.is_displayed():
                    button_text = (button.text or button.get_attribute('aria-label') or '').lower()
                    
                    # Skip disabled buttons
                    if button.get_attribute('disabled') or 'disabled' in button.get_attribute('class'):
                        continue
                    
                    logger.info(f"Clicking button: {button_text} ({selector})")
                    if element_handler.safe_click(button):
                        human_sim.human_delay(1, 3)
                        
                        # Check if this was a submit button
                        if any(word in button_text for word in ['submit', 'complete', 'finish']):
                            return 'submitted'
                        
                        return True
        except Exception as e:
            logger.debug(f"Error with selector {selector}: {e}")
            continue
    
    logger.warning("No actionable buttons found")
    return False