import random

from dataclasses import dataclass, field

@dataclass
class Config:
    """ Configuration Data """
    WEB_DRIVER_TIMEOUT: int = 10
    FIREFOX_PROFILE_PATH_PATTERN: str = r"^C:\\Users\\[^\\]+\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\[^\\]+$"
    SLEEP_TIMEOUT: (int | float) = random.uniform(2, 5)
    RESUME_PATH: str = str()
    FIREFOX_DRIVER_PATH = "./geckodriver-v0.36.0-win64/geckodriver.exe"
    WEB_DRIVER_SCROLL_BEHAVIOUR: str = "arguments[0].scrollIntoView({behaviour: 'smooth', block: 'center'});"
    SAVE_JOB_PREFERENCE: str = str()
