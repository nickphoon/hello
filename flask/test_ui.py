from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def test_homepage():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Remote(
        command_executor='http://selenium-hub:4444/wd/hub',
        options=options
    )
    
    driver.get("http://flask-app-test:5000")
    assert "Welcome" in driver.title
    
    # Example of interacting with a form
    password_input = driver.find_element(By.NAME, "password")
    password_input.send_keys("StrongPass123")
    password_input.send_keys(Keys.RETURN)
    
    # Check for a specific element or text in the response
    assert "Welcome" in driver.page_source
    
    driver.quit()
