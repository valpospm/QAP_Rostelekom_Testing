import pickle
import pytest
from pages.auth import *
from pages.settings import *
from pages.settings import valid_phone, valid_login, valid_password, invalid_ls, valid_email, valid_pass_reg


@pytest.mark.auth
@pytest.mark.parametrize('username', [valid_phone, valid_email, valid_login, invalid_ls],
                         ids=['phone', 'email', 'login', 'ls'])
def test_active_tab(browser, username):
    """Тест-кейс #TC-RT-004 - Автоматическое изменение типа авторизации (по телефону, почте, логину или лицевому счету)
    при вводе соответствующего типа данных в первое поле формы авторизации"""
    page = AuthPage(browser)
    page.enter_username(username)
    page.enter_password(valid_password)
    if username == valid_phone:
        assert browser.find_element(*AuthLocators.AUTH_ACTIVE_TAB).text == 'Телефон'
    elif username == valid_email:
        assert browser.find_element(*AuthLocators.AUTH_ACTIVE_TAB).text == 'Почта'
    elif username == valid_login:
        assert browser.find_element(*AuthLocators.AUTH_ACTIVE_TAB).text == 'Логин'
    else:
        assert browser.find_element(*AuthLocators.AUTH_ACTIVE_TAB).text == 'Лицевой счет'


@pytest.mark.auth
@pytest.mark.positive
def test_auth_page_email_valid(browser):
    """Тест-кейс #TC-RT-006 - Возможность авторизации на веб-сайте с валидными данными (валидный email и пароль)"""
    page = AuthPage(browser)
    page.enter_username(valid_email)
    page.enter_password(valid_pass_reg)
    time.sleep(25)  # на случай появления Captcha, необходимости ее ввода вручную
    page.btn_click_enter()
    page.driver.save_screenshot('auth_by_email.png')

    with open('my_cookies.txt', 'wb') as cookies:
        pickle.dump(browser.get_cookies(), cookies)

    assert page.get_relative_link() == '/account_b2c/page'


@pytest.mark.auth
@pytest.mark.negative
def test_auth_page_phone_empty_username(browser):
    """Тест-кейс #TC-RT-007 - Вывод запроса на ввод данных в ходе авторизации на веб-сайте при вводе пустого значения
    телефона/почты/логина/лицевого счета и валидного пароля"""
    page = AuthPage(browser)
    page.enter_username('')
    page.enter_password(valid_password)
    page.btn_click_enter()
    browser.implicitly_wait(10)

    error_mess = browser.find_element(*AuthLocators.AUTH_MESS_ERROR)
    assert error_mess.text == 'Введите номер телефона' or \
           error_mess.text == 'Введите адрес, указанный при регистрации' or \
           error_mess.text == 'Введите логин, указанный при регистрации' or \
           error_mess.text == 'Введите номер вашего лицевого счета'


@pytest.mark.auth
@pytest.mark.negative
@pytest.mark.parametrize('username', [valid_phone, valid_email, valid_login],
                         ids=['valid phone', 'valid login', 'valid email'])
def test_auth_page_fake_password(browser, username):
    """Тест-кейс #TC-RT-009 - Отказ в авторизации на веб-сайте при вводе валидного телефона/почты/логина
    и невалидного пароля"""
    page = AuthPage(browser)
    page.enter_username(username)
    page.enter_password(fake_password)
    page.btn_click_enter()
    browser.implicitly_wait(20)

    error_mess = browser.find_element(*AuthLocators.AUTH_FORM_ERROR)
    forgot_pass = browser.find_element(*AuthLocators.AUTH_FORGOT_PASSWORD)

    assert error_mess.text == 'Неверный логин или пароль' and \
           page.check_color(forgot_pass) == '#ff4f12'

