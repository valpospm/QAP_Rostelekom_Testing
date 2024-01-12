from devmail import DevMail


class RegistrationEmail:
    """На сервисе DeveloperMail отправляем запрос на создание виртуального email
    для регистрации в личном кабинете "Ростелеком"."""

    def get_email_id_letter(self):

        """Получаем валидный адрес электронной почты и mail_id"""

        mailbox = DevMail()
        result_email = mailbox.create()
        result_id = mailbox.getmailids()
        return result_email, result_id

    def get_reg_code(self, ids: str):

        """Получаем письмо с кодом регистрации от Ростелекома (id=ids)"""

        mailbox = DevMail()
        result_code = mailbox.getmail(ids, raw=True)
        return result_code
