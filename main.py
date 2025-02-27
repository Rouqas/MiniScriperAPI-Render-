from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

app = FastAPI()

# Replace these with your LinkedIn credentials
LINKEDIN_EMAIL = "schmoopiebisque@gmail.com"
LINKEDIN_PASSWORD = "schmoopieB"

class ScrapeRequest(BaseModel):
    profile_url: str

def login_to_linkedin(driver):
    """ Logs into LinkedIn using Selenium. """
    driver.get("https://www.linkedin.com/login")


        # Add LinkedIn session cookie (Replace 'YOUR_COOKIE_VALUE' with the copied value)
    driver.add_cookie({
        "name": "li_at",
        "value": "AQEDAVfQdfwBtk4mAAABlSWHB60AAAGVSZOLrU4AdhCuReVr1Rk8sp3BxpXoSvVMIx135eftTzVMpfYYm-GLQAVdLlfdLHWwnrCRPA34iMAbfrpYm2b_ib2yfW0ynB4xakiF5pmaVnvLoMp6whM9NPTO",  # Paste the copied `li_at` cookie value here
        "domain": ".linkedin.com"
    })

    # Refresh the page to apply the cookie
    driver.get("https://www.linkedin.com/feed/")

    # Verify successful login
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.profile-card-member-details"))
        )
        print("Successfully logged in using cookies!")
    except:
        print("Failed to log in with cookies.")
        raise HTTPException(status_code=500, detail="Failed to log in using LinkedIn session cookie")
    
    # try:
    #     # Wait until the login fields are visible
    #     WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))

    #     # Enter email
    #     email_field = driver.find_element(By.ID, "username")
    #     email_field.send_keys(LINKEDIN_EMAIL)

    #     # Enter password
    #     password_field = driver.find_element(By.ID, "password")
    #     password_field.send_keys(LINKEDIN_PASSWORD)

    #     # Click the login button
    #     login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    #     login_button.click()

    #     # Wait for the home page to load completely
    #     WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.feed-identity-module")))
    #     print("Successfully logged in!")

    # except Exception as e:

    #     print("Login failed:", e)
    #     raise HTTPException(status_code=500, detail="Failed to log in to LinkedIn")

@app.post("/scrape")
async def scrape_profile(request: ScrapeRequest):
    try:
        # Set up Chrome options for headless operation
        options = Options()
        options.add_argument("--headless")  # Run in headless mode (no UI)
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # Specify Chrome binary location (Adjust the path for Windows)
        chrome_path = "/usr/bin/google-chrome"
        options.binary_location = chrome_path

        # Initialize ChromeDriver using WebDriver Manager
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        # Log in to LinkedIn
        login_to_linkedin(driver)

        # Open the LinkedIn profile page
        driver.get(request.profile_url)

        # disabled to reduce waiting
        # # Wait until the profile loads
        # WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.CSS_SELECTOR, "div.text-body-medium"))
        # )

        # Extract headline
        headline_element = driver.find_element(By.CSS_SELECTOR, "div.text-body-medium")
        headline = headline_element.text

        driver.quit()
        return {"headline": headline}

    except Exception as e:
        try:
            driver.quit()
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=str(e))
    
# Run the FastAPI app on port 8000 on Render/Railway
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

