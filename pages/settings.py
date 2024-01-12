"""Действующие данные для авторизации в системе"""
import os
from dotenv import load_dotenv
from faker import Faker
import string
load_dotenv()


"""Фейковые данные для авторизации в системе"""
fake_ru = Faker('ru_RU')
fake_firstname = fake_ru.first_name()
fake_lastname = fake_ru.last_name()
fake_phone = fake_ru.phone_number()
fake = Faker()
fake_password = fake.password()
fake_login = fake.user_name()
fake_email = fake.email()


valid_phone = os.getenv('phone')
valid_login = os.getenv('login')
valid_password = os.getenv('password')
invalid_ls = '123456789123'

valid_email = 'postnikov_v_v@mail.ru'
valid_pass_reg = 'hjy_980$FnIt'


def generate_string_rus(n):
    return 'б' * n


def generate_string_en(n):
    return 'x' * n


def english_chars():
    return 'qwertyuiopasdfghjklzxcvbnm'


def russian_chars():
    return 'абвгдеёжзиклмнопрстуфхцчшщъыьэюя'


def special_chars():
    return f'{string.punctuation}'