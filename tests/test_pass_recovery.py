from pages.registration_email import RegistrationEmail
from pages.auth import *
from pages.settings import *
from selenium.webdriver.common.keys import Keys
import time
import pytest


@pytest.mark.pass_recovery
def test_forgot_password_page_positive(browser):
    """Тест-кейс #TC-RT-016 - Возможность восстановления пароля с валидной электронной почтой"""
    sign_at = valid_email.find('@')
    mail_name = valid_email[0:sign_at]

    page = NewPassPage(browser)
    page.enter_username(valid_email)
    time.sleep(25)     # Время на прохождение CAPTCHA вручную
    page.btn_click_continue()

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
        browser.find_elements(*NewPassLocators.NEWPASS_ONETIME_CODE)[i].send_keys(reg_code[i])
        browser.implicitly_wait(5)
    time.sleep(10)
    new_pass = fake_password
    browser.find_element(*NewPassLocators.NEWPASS_NEW_PASS).send_keys(new_pass)
    time.sleep(3)
    browser.find_element(*NewPassLocators.NEWPASS_NEW_PASS_CONFIRM).send_keys(new_pass)
    browser.find_element(*NewPassLocators.NEWPASS_BTN_SAVE).click()
    time.sleep(60)
    print(browser.current_url)

    assert page.get_relative_link() == '/auth/realms/b2c/login-actions/authenticate'

    """В случае успешной смены пароля, перезаписываем его в файл settings"""
    with open(r"../pages/settings.py", 'r', encoding='utf8') as file:
        lines = []
        for line in file.readlines():
            if 'valid_pass_reg' in line:
                lines.append(f"valid_pass_reg = '{fake_password}'\n")
            else:
                lines.append(line)
    with open(r"../pages/settings.py", 'w', encoding='utf8') as file:
        file.writelines(lines)


def test_forgot_password_page_negative(browser):
    """Тест-кейсы #TC-RT-021,022,023 - Негативные тест-кейсы восстановления пароля: новый пароль в некорректном формате,
    не совпдает в обоих полях формы, является действующим паролем"""
    sign_at = valid_email.find('@')
    mail_name = valid_email[0:sign_at]

    page = NewPassPage(browser)
    page.enter_username(valid_email)
    time.sleep(25)     # Время на прохождение CAPTCHA вручную
    page.btn_click_continue()

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
        browser.find_elements(*NewPassLocators.NEWPASS_ONETIME_CODE)[i].send_keys(reg_code[i])
        browser.implicitly_wait(5)
    time.sleep(10)

    elem_new_pass = browser.find_element(*NewPassLocators.NEWPASS_NEW_PASS)
    elem_conf_pass = browser.find_element(*NewPassLocators.NEWPASS_NEW_PASS_CONFIRM)

    def input_new_pass(new_pass):
        elem_new_pass.send_keys(Keys.COMMAND, 'a')
        elem_new_pass.send_keys(Keys.DELETE)
        elem_new_pass.send_keys(new_pass)
        time.sleep(3)
        elem_conf_pass.send_keys(Keys.COMMAND, 'a')
        elem_conf_pass.send_keys(Keys.DELETE)
        elem_conf_pass.send_keys(new_pass)
        time.sleep(3)

        """Новый пароль - менее 8 символов"""
        new_pass = valid_pass_reg[0:7]
        input_new_pass(new_pass)

        error_mess = browser.find_element(*AuthLocators.AUTH_MESS_ERROR)
        assert error_mess.text == 'Длина пароля должна быть не менее 8 символов'

        """Новый пароль - более 20 символов"""
        new_pass = valid_pass_reg[0:7] * 3
        input_new_pass(new_pass)

        error_mess = browser.find_element(*AuthLocators.AUTH_MESS_ERROR)
        assert error_mess.text == 'Длина пароля должна быть не более 20 символов'

        """Новый пароль - пароль не содержит заглавные буквы"""
        new_pass = valid_pass_reg.lower()
        input_new_pass(new_pass)

        error_mess = browser.find_element(*AuthLocators.AUTH_MESS_ERROR)
        assert error_mess.text == 'Пароль должен содержать хотя бы одну заглавную букву'

        """Новый пароль - пароль включает в себя кириллицу"""
        new_pass1 = f'{valid_pass_reg}{generate_string_rus(8)}'
        input_new_pass(new_pass1)

        error_mess = browser.find_element(*AuthLocators.AUTH_MESS_ERROR)
        assert error_mess.text == 'Пароль должен содержать только латинские буквы'

        """Новый пароль - пароль не содержит ни одной цифры или спецсимвола"""
        new_pass = valid_pass_reg
        for n in new_pass:
            if n.isdigit() or n in special_chars():
                new_pass = new_pass.replace(n, 'x')
        input_new_pass(new_pass)

        error_mess = browser.find_element(*AuthLocators.AUTH_MESS_ERROR)
        assert error_mess.text == 'Пароль должен содержать хотя бы 1 спецсимвол или хотя бы одну цифру'

        """Новый пароль отличается от пароля в поле 'Подтверждение пароля'."""
        elem_new_pass.send_keys(Keys.COMMAND, 'a')
        elem_new_pass.send_keys(Keys.DELETE)
        new_pass = f'{valid_pass_reg[0:8]}{generate_string_en(2)}'
        elem_new_pass.send_keys(new_pass)
        time.sleep(3)

        elem_conf_pass.send_keys(Keys.COMMAND, 'a')
        elem_conf_pass.send_keys(Keys.DELETE)
        new_conf_pass = f'{valid_pass_reg[0:8]}{generate_string_en(4)}'
        elem_conf_pass.send_keys(new_conf_pass)
        time.sleep(3)

        browser.find_element(*NewPassLocators.NEWPASS_BTN_SAVE).click()

        error_mess = browser.find_element(*AuthLocators.AUTH_MESS_ERROR)
        assert error_mess.text == 'Пароли не совпадают'

        """Новый пароль - идентичен предыдущему"""
        new_pass = valid_pass_reg
        input_new_pass(new_pass)
        browser.find_element(*NewPassLocators.NEWPASS_BTN_SAVE).click()

        error_mess = browser.find_element(*AuthLocators.AUTH_FORM_ERROR)
        assert error_mess.text == 'Этот пароль уже использовался, укажите другой пароль'
