import time

from typing import Optional
from selenium.webdriver import Firefox
from plyer import notification
from colorama import init, Fore
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from config import Config

class CareerFlow:
    def __init__(self, web_driver: Optional[Firefox]) -> None:
        init(autoreset=True)

        self.web_driver: Optional[Firefox] = web_driver
        self.config: Config = Config()

    @staticmethod
    def _display_notification(title: str = "", message: str = "", timeout: int = 10) -> None:
        """ Displays Custom Notifications to the User """
        try:
            notification.notify(title=title, message=message, app_name="AutoApply", timeout=timeout)
        except Exception as e:
            print(Fore.RED + f"Unable to show notifications. {e}")

    def _glassdoor_read_job_details(self) -> list[str]:
        """
            Fetch all the required data to save Job at CareerFlow
            :return: Return a 'List' of 'String' of Job Data
        """
        # Switch to the Job Posing page & copy the Data
        time.sleep(self.config.SLEEP_TIMEOUT)
        self.web_driver.switch_to.window(self.web_driver.window_handles[0])

        time.sleep(self.config.SLEEP_TIMEOUT)
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//button/span[text()='Show more']"))).click()

        return [self.web_driver.find_element(By.TAG_NAME, "h1").text,
                               self.web_driver.find_element(By.TAG_NAME, "h4").text,
                               self.web_driver.current_url,
                               self.web_driver.find_element(By.XPATH, "//div[@data-test='detailSalary']").text,
                               self.web_driver.find_element(By.XPATH, "//div[@data-test='location']").text,
                               self.web_driver.find_element(By.XPATH, "//div[contains(@class,'JobDetails_jobDescription')]").text]

    def _glassdoor_fill_career_flow_job_form(self, job_data: list[str]) -> None:
        """ Fills the Job Details at CareerFlow """
        # Click on "Job Tracker"
        time.sleep(self.config.SLEEP_TIMEOUT)
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Job Tracker']"))).click()

        # Click on "Add Job"
        time.sleep(self.config.SLEEP_TIMEOUT)
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Add Job']"))).click()

        # Enter Job title
        time.sleep(self.config.SLEEP_TIMEOUT)
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "basic_jobtitle"))).send_keys(job_data[0])

        # Enter Company name
        time.sleep(self.config.SLEEP_TIMEOUT)
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "basic_companyName"))).send_keys(job_data[1])

        # Enter Job URL
        time.sleep(self.config.SLEEP_TIMEOUT)
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "basic_joburl"))).send_keys(job_data[2])

        # Click on Status
        time.sleep(self.config.SLEEP_TIMEOUT)
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.ant-select-selector"))).click()
        time.sleep(self.config.SLEEP_TIMEOUT)
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class,'ant-select-item-option-content') and text()='Applied']"))).click()

        # Enter Salary
        time.sleep(self.config.SLEEP_TIMEOUT)
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "basic_salary"))).send_keys(job_data[3])

        # Enter Job Location
        self.web_driver.execute_script(self.config.WEB_DRIVER_SCROLL_BEHAVIOUR, self.web_driver.find_element(By.ID, "basic_location"))
        time.sleep(self.config.SLEEP_TIMEOUT)
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "basic_location"))).send_keys(job_data[4])

        # Enter Job Description
        self.web_driver.execute_script(self.config.WEB_DRIVER_SCROLL_BEHAVIOUR, self.web_driver.find_element(By.CSS_SELECTOR, "#basic_description .ql-editor"))
        time.sleep(self.config.SLEEP_TIMEOUT)
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#basic_description .ql-editor"))).send_keys(job_data[5])

        # Click on Save button
        self.web_driver.execute_script(self.config.WEB_DRIVER_SCROLL_BEHAVIOUR, self.web_driver.find_element(By.XPATH, "//span[text()='Submit']"))
        time.sleep(self.config.SLEEP_TIMEOUT)
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Submit']")))

    def glassdoor_save_to_career_flow(self) -> None:
        """ Save Job on CareerFlow """
        # Open CareerFlow Page
        time.sleep(self.config.SLEEP_TIMEOUT)
        self.web_driver.execute_script("window.open('https://app.careerflow.ai/board');")

        # Get the Title of the Page
        time.sleep(self.config.SLEEP_TIMEOUT)
        if "Login" in self.web_driver.title:
            self._display_notification(title="Unable to Save Job to CareerFlow", message="Please Login at CareerFlow to save the Job.")

            return

        job_data: list[str] = self._glassdoor_read_job_details()

        # Switch to CareerFlow page
        self.web_driver.switch_to.window(self.web_driver.window_handles[2])

        self._glassdoor_fill_career_flow_job_form(job_data)
