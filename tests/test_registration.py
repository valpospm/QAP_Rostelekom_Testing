from pages.registration_email import RegistrationEmail
from pages.auth import *
from selenium.webdriver.common.by import By
from pages.settings import *
from devmail import DevMail
import time
import pytest


class TestRegistration:

    """Проверка формы регистрации на сайте"""

    # Выносим данные в тело класса для доступа к значениям переменных из всех функций класса:

    mailbox = DevMail()
    result_email = mailbox.create()  # запрос на получение валидного почтового ящика
    email_reg = result_email[0]  # из запроса получаем валидный email

    @pytest.mark.reg
    def test_get_registration_valid(self, browser):
        """Тест-кейс #TC-RT-032 - Возможность зарегистрировать нового пользователя с данными корректного формата"""
        sign_at = valid_email.find('@')
        mail_name = valid_email[0:sign_at]

        """Активируем окно ввода данных для прохождения регистрации на сайте"""
        # Нажимаем на кнопку Зарегистрироваться:
        page = AuthPage(browser)
        page.enter_reg_page()
        browser.implicitly_wait(2)
        assert page.get_relative_link() == '/auth/realms/b2c/login-actions/registration'
        page = RegPage(browser)
        # Вводим имя:
        page.enter_firstname(fake_firstname)
        browser.implicitly_wait(5)
        # Вводим фамилию:
        page.enter_lastname(fake_lastname)
        browser.implicitly_wait(5)
        # Вводим адрес почты/Email:
        page.enter_email(self.email_reg)
        browser.implicitly_wait(3)
        # Вводим пароль:
        page.enter_password(fake_password)
        browser.implicitly_wait(3)
        # Вводим подтверждение пароля:
        page.enter_pass_conf(fake_password)
        browser.implicitly_wait(3)
        # Нажимаем на кнопку 'Зарегистрироваться':
        page.btn_click()
        time.sleep(30)  # Ожидание получения письма с одноразовым кодом.

        """Проверяем почтовый ящик на наличие писем и достаём ID последнего письма"""
        result_id = RegistrationEmail().get_email_id_letter()
        # Получаем id письма с кодом из почтового ящика:
        id_letter = result_id[0].get('id')
        # Проверяем полученные данные
        assert id_letter > 0, "id_letter > 0 error"

        """Получаем код регистрации из письма от Ростелекома"""
        result_code = RegistrationEmail().get_reg_code(mail_name)

        # Получаем body из текста письма:
        text_body = result_code.get('body')
        # Извлекаем код из текста методом find:
        reg_code = text_body[text_body.find('Ваш код: ') + len('Ваш код: '):
                             text_body.find('Ваш код: ') + len('Ваш код: ') + 6]
        # Проверяем полученные данные
        assert reg_code != '', "reg_code != [] error"

        reg_digit = [int(char) for char in reg_code]
        print(reg_digit)
        browser.implicitly_wait(30)
        for i in range(0, 6):
            browser.find_elements(By.XPATH, '//input[@inputmode="numeric"]')[i].send_keys(reg_code[i])
            browser.implicitly_wait(5)
        browser.implicitly_wait(30)

        """Проверяем, что регистрация пройдена и пользователь перенаправлен в личный кабинет"""
        assert page.get_relative_link() == '/account_b2c/page', 'Регистрация НЕ пройдена'
        page.driver.save_screenshot('reg_done.png')

        """В случае успешной регистрации, перезаписываем созданные пару email/пароль в файл settings"""
        page.driver.save_screenshot('reg_done.png')
        print(self.email_reg, fake_password)
        with open(r"../pages/Settings.py", 'r', encoding='utf8') as file:
            lines = []
            print(lines)
            for line in file.readlines():
                if 'valid_email' in line:
                    lines.append(f"valid_email = '{str(self.email_reg)}'\n")
                elif 'valid_pass_reg' in line:
                    lines.append(f"valid_pass_reg = '{fake_password}'\n")
                else:
                    lines.append(line)
        with open(r"../pages/Settings.py", 'w', encoding='utf8') as file:
            file.writelines(lines)


@pytest.mark.parametrize('firstname', ['', generate_string_rus(1), generate_string_rus(31),
                                       generate_string_rus(256), english_chars(),
                                       special_chars(), 11111],
                         ids=['empty', 'one char', '31 chars', '256 chars', 'english',
                              'special', 'number'])
def test_get_registration_invalid_format_firstname(browser, firstname):

    """Тест-кейс #TC-RT-026 - Поле ввода имени нового пользователя формы регистрации - негативный сценарий
    (некорректный формат имени)"""

    # Нажимаем на кнопку Зарегистрироваться:
    page = AuthPage(browser)
    page.enter_reg_page()
    browser.implicitly_wait(2)
    assert page.get_relative_link() == '/auth/realms/b2c/login-actions/registration'

    page = RegPage(browser)
    # Вводим имя:
    page.enter_firstname(firstname)
    browser.implicitly_wait(5)
    # Вводим фамилию:
    page.enter_lastname(fake_lastname)
    browser.implicitly_wait(5)
    # Вводим адрес почты/Email:
    page.enter_email(fake_email)
    browser.implicitly_wait(3)
    # Вводим пароль:
    page.enter_password(fake_password)
    browser.implicitly_wait(3)
    # Вводим подтверждение пароля:
    page.enter_pass_conf(fake_password)
    browser.implicitly_wait(3)
    # Нажимаем на кнопку 'Зарегистрироваться':
    page.btn_click()

    error_mess = browser.find_element(*AuthLocators.AUTH_MESS_ERROR)

    assert error_mess.text == 'Необходимо заполнить поле кириллицей. От 2 до 30 символов.'


@pytest.mark.parametrize('lastname', ['', generate_string_rus(1), generate_string_rus(31),
                                      generate_string_rus(256), english_chars(),
                                      special_chars(), 11111],
                         ids=['empty', 'one char', '31 chars', '256 chars', 'english',
                              'special', 'number'])
def test_get_registration_invalid_format_lastname(browser, lastname):
    """Тест-кейс #TC-RT-027 - Поле ввода фамилии нового пользователя формы регистрации - негативный сценарий
    (некорректный формат фамилии)"""

    # Нажимаем на кнопку Зарегистрироваться:
    page = AuthPage(browser)
    page.enter_reg_page()
    browser.implicitly_wait(2)
    assert page.get_relative_link() == '/auth/realms/b2c/login-actions/registration'

    page = RegPage(browser)
    # Вводим имя:
    page.enter_firstname(fake_firstname)
    browser.implicitly_wait(5)
    # Вводим фамилию:
    page.enter_lastname(lastname)
    browser.implicitly_wait(5)
    # Вводим адрес почты/Email:
    page.enter_email(fake_email)
    browser.implicitly_wait(3)
    # Вводим пароль:
    page.enter_password(fake_password)
    browser.implicitly_wait(3)
    # Вводим подтверждение пароля:
    page.enter_pass_conf(fake_password)
    browser.implicitly_wait(3)
    # Нажимаем на кнопку 'Зарегистрироваться':
    page.btn_click()

    error_mess = browser.find_element(*AuthLocators.AUTH_MESS_ERROR)
    assert error_mess.text == 'Необходимо заполнить поле кириллицей. От 2 до 30 символов.'


@pytest.mark.parametrize('phone', ['', 1, 7111111111, generate_string_rus(11), special_chars()],
                         ids=['empty', 'one digit', 'no 1 digit', 'string', 'specials'])
def test_get_registration_invalid_format_phone(browser, phone):
    """Тест-кейс #TC-RT-028 - Поле ввода Email или мобильного телефона нового пользователя формы регистрации -
    негативный сценарий (некорректный формат телефона)"""

    # Нажимаем на кнопку Зарегистрироваться:
    page = AuthPage(browser)
    page.enter_reg_page()
    browser.implicitly_wait(2)
    assert page.get_relative_link() == '/auth/realms/b2c/login-actions/registration'

    page = RegPage(browser)
    # Вводим имя:
    page.enter_firstname(fake_firstname)
    browser.implicitly_wait(5)
    # Вводим фамилию:
    page.enter_lastname(fake_lastname)
    browser.implicitly_wait(5)
    # Вводим номер телефона:
    page.enter_email(phone)
    browser.implicitly_wait(3)
    # Вводим пароль:
    page.enter_password(fake_password)
    browser.implicitly_wait(3)
    # Вводим подтверждение пароля:
    page.enter_pass_conf(fake_password)
    browser.implicitly_wait(3)
    # Нажимаем на кнопку 'Зарегистрироваться':
    page.btn_click()

    error_mess = browser.find_element(*AuthLocators.AUTH_MESS_ERROR)
    assert error_mess.text == 'Введите телефон в формате +7ХХХХХХХХХХ или +375XXXXXXXXX, ' \
                              'или email в формате example@email.ru'


@pytest.mark.parametrize('email', ['', '@', '@.', '.', generate_string_rus(20), f'{russian_chars()}@mail.ru',
                                   11111],
                         ids=['empty', 'at', 'at point', 'point', 'string', 'russian',
                              'numbers'])
def test_get_registration_invalid_format_email(browser, email):
    """Тест-кейс #TC-RT-028 - Поле ввода Email или мобильного телефона нового пользователя формы регистрации -
    негативный сценарий (некорректный формат электронной почты)"""
    # Нажимаем на кнопку Зарегистрироваться:
    page = AuthPage(browser)
    page.enter_reg_page()
    browser.implicitly_wait(2)
    assert page.get_relative_link() == '/auth/realms/b2c/login-actions/registration'

    page = RegPage(browser)
    # Вводим имя:
    page.enter_firstname(fake_firstname)
    browser.implicitly_wait(5)
    # Вводим фамилию:
    page.enter_lastname(fake_lastname)
    browser.implicitly_wait(5)
    # Вводим адрес почты/Email:
    page.enter_email(email)
    browser.implicitly_wait(3)
    # Вводим пароль:
    page.enter_password(fake_password)
    browser.implicitly_wait(3)
    # Вводим подтверждение пароля:
    page.enter_pass_conf(fake_password)
    browser.implicitly_wait(3)
    # Нажимаем на кнопку 'Зарегистрироваться':
    page.btn_click()

    error_mess = browser.find_element(*AuthLocators.AUTH_MESS_ERROR)
    assert error_mess.text == 'Введите телефон в формате +7ХХХХХХХХХХ или +375XXXXXXXXX, ' \
                              'или email в формате example@email.ru'


@pytest.mark.parametrize('address', [valid_phone, valid_email],
                         ids=['living phone', 'living email'])
def test_get_registration_living_account(browser, address):
    """Тест-кейс #TC-RT-031 - Невозможность зарегистрировать нового пользователя при указании в форме регистрации
    валидного адреса электронной почты действующего пользователя"""

    # Нажимаем на кнопку Зарегистрироваться:
    page = AuthPage(browser)
    page.enter_reg_page()
    browser.implicitly_wait(2)
    assert page.get_relative_link() == '/auth/realms/b2c/login-actions/registration'

    page = RegPage(browser)
    # Вводим имя:
    page.enter_firstname(fake_firstname)
    browser.implicitly_wait(5)
    # Вводим фамилию:
    page.enter_lastname(fake_lastname)
    browser.implicitly_wait(5)
    # Вводим адрес почты/Email:
    page.enter_email(address)
    browser.implicitly_wait(3)
    # Вводим пароль:
    page.enter_password(fake_password)
    browser.implicitly_wait(3)
    # Вводим подтверждение пароля:
    page.enter_pass_conf(fake_password)
    browser.implicitly_wait(3)
    # Нажимаем на кнопку 'Зарегистрироваться':
    page.btn_click()

    card_modal_title = browser.find_element(*RegLocators.REG_CARD_MODAL)

    assert card_modal_title.text == 'Учётная запись уже существует'


def test_get_registration_diff_pass_and_pass_conf(browser):

    """Тест-кейс #TC-RT-030 - Невозможность зарегистрировать нового пользователя при указании в форме регистрации
    разных паролей корректного формата в соответствующие поля формы (значения полей не совпадают друг с другом)"""

    page = AuthPage(browser)
    page.enter_reg_page()
    browser.implicitly_wait(2)
    assert page.get_relative_link() == '/auth/realms/b2c/login-actions/registration'

    page = RegPage(browser)
    # Вводим имя:
    page.enter_firstname(fake_firstname)
    browser.implicitly_wait(5)
    # Вводим фамилию:
    page.enter_lastname(fake_lastname)
    browser.implicitly_wait(5)
    # Вводим адрес почты/Email:
    page.enter_email(fake_email)
    browser.implicitly_wait(3)
    # Вводим пароль:
    page.enter_password(fake_password)
    browser.implicitly_wait(3)
    # Вводим подтверждение пароля:
    page.enter_pass_conf(valid_pass_reg)
    browser.implicitly_wait(3)
    # Нажимаем на кнопку 'Зарегистрироваться':
    page.btn_click()

    error_mess = browser.find_element(*AuthLocators.AUTH_MESS_ERROR)
    assert error_mess.text == 'Пароли не совпадают'
