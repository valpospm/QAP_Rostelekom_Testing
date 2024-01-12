import time
import pytest
from selenium import webdriver
from faker import Faker


@pytest.fixture(autouse=True)
def browser():
    driver = webdriver.Edge(executable_path='msedgedriver.exec')

    yield driver
    driver.quit()
