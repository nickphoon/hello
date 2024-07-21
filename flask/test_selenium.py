import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

class FlaskAppTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        options = Options()
        options.add_argument("--headless")  # Run in headless mode
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument('--remote-debugging-port=9222')
        cls.driver = webdriver.Chrome(options=options)
        cls.driver.implicitly_wait(10)
        cls.base_url = 'http://127.0.0.1:5000'

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def test_weak_password(self):
        self.driver.get(self.base_url)
        password_input = self.driver.find_element(By.NAME, 'password')
        password_input.send_keys('weakpass')
        password_input.send_keys(Keys.RETURN)
        error_message = self.driver.find_element(By.XPATH, "//p[@style='color:red;']")
        self.assertIn('Password does not meet the requirements.', error_message.text)

    def test_strong_password(self):
        self.driver.get(self.base_url)
        password_input = self.driver.find_element(By.NAME, 'password')
        password_input.send_keys('Str0ngPassw0rd!')
        password_input.send_keys(Keys.RETURN)
        welcome_message = self.driver.find_element(By.TAG_NAME, 'h1')
        self.assertIn('Welcome!', welcome_message.text)

if __name__ == '__main__':
    unittest.main()
