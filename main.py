from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import requests
import time
import os
from datetime import datetime

# Webhook URL (replace with your actual webhook URL)
WEBHOOK_URL = 'YOUR_WEBHOOK_URL'

# URL to screenshot
TARGET_URL = 'https://explorer.duinocoin.com'

def take_screenshot():
    # Set up Chrome options for headless operation on Linux
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')  # Use new headless mode for better compatibility
    options.add_argument('--no-sandbox')  # Required for Linux environments (e.g., root user issues)
    options.add_argument('--disable-dev-shm-usage')  # Avoid shared memory issues
    options.add_argument('--disable-gpu')  # Disable GPU acceleration (not needed in headless)
    options.add_argument('--window-size=1920,1080')  # Set window size for consistent screenshots
    options.add_argument('--disable-extensions')  # Disable extensions for stability
    options.add_argument('--disable-infobars')  # Disable infobars
    options.add_argument('--disable-setuid-sandbox')  # Additional sandboxing disable for Linux

    # Initialize WebDriver with ChromeDriver
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    except Exception as e:
        print(f'Error initializing WebDriver: {e}')
        return None

    try:
        # Navigate to the target URL
        driver.get(TARGET_URL)
        
        # Wait for the page to load (adjust time if needed)
        time.sleep(5)
        
        # Generate a unique filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        screenshot_path = f'screenshot_{timestamp}.png'
        
        # Take screenshot and save it
        driver.save_screenshot(screenshot_path)
        print(f'Screenshot saved as {screenshot_path}')
        
        return screenshot_path
    
    except Exception as e:
        print(f'Error taking screenshot: {e}')
        return None
    
    finally:
        # Close the browser
        driver.quit()

def send_to_webhook(screenshot_path):
    if not screenshot_path or not os.path.exists(screenshot_path):
        print('No screenshot to send')
        return

    try:
        # Open the screenshot file in binary mode
        with open(screenshot_path, 'rb') as f:
            files = {'file': (screenshot_path, f, 'image/png')}
            # Send the screenshot to the webhook
            response = requests.post(WEBHOOK_URL, files=files)
            
            if response.status_code in (200, 204):
                print('Screenshot sent to webhook successfully')
            else:
                print(f'Failed to send screenshot to webhook: {response.status_code} - {response.text}')
    
    except Exception as e:
        print(f'Error sending screenshot to webhook: {e}')
    
    finally:
        # Clean up the screenshot file
        if os.path.exists(screenshot_path):
            try:
                os.remove(screenshot_path)
                print(f'Screenshot file {screenshot_path} deleted')
            except Exception as e:
                print(f'Error deleting screenshot file: {e}')

def main():
    print('Starting screenshot bot...')
    while True:
        try:
            # Take a screenshot
            screenshot_path = take_screenshot()
            
            # Send the screenshot to the webhook
            send_to_webhook(screenshot_path)
            
            # Wait for 5 minutes (300 seconds)
            print('Waiting for 5 minutes...')
            time.sleep(300)
        
        except Exception as e:
            print(f'Error in main loop: {e}')
            # Wait for 5 minutes before retrying in case of an error
            time.sleep(300)

if __name__ == '__main__':
    main()
