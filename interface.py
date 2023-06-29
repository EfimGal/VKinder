import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from config import comunity_token, acces_token
from core import VkTools
from data_store import Viewed
from data_store import engine


class BotInterface():

    def __init__(self, comunity_token, acces_token):
        self.interface = vk_api.VkApi(token=comunity_token)
        self.api = VkTools(acces_token)
        self.longpoll = VkLongPoll(self.interface)
        self.offset = 0
        self.params = None
        self.users = []
        #self.viewed = Viewed

    def message_send(self, user_id, message, attachment=None):
        self.interface.method('messages.send',
                              {'user_id': user_id,
                               'message': message,
                               'attachment': attachment,
                               'random_id': get_random_id()
                               }
                              )

    def event_handler(self):

        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()
                if command == 'привет':
                    self.params = self.api.get_profile_info(event.user_id)
                    self.message_send(event.user_id, f'Привет, {self.params["name"]}!')
                    if self.params.get('city') is None:
                        self.params['city'] = self.ask_city(event.user_id)
                    if self.params.get('bdate') is None:
                        self.params['bdate'] = self.ask_bdate(event.user_id)

                elif command == 'поиск':
                    if self.users:
                        while len(self.users) >= 1:
                            user = self.users.pop()
                            if Viewed.check_user(engine, event.user_id, user['id']):
                                continue
                            photos_user = self.api.get_photos(user['id'])
                            attachment = ''
                            for photo in photos_user:
                                attachment += f'photo{photo["owner_id"]}_{photo["id"]},'
                            self.message_send(event.user_id,
                                              f'Встречайте: {user["name"]}\nСсылка: vk.com/id{user["id"]}',
                                              attachment=attachment
                                              )
                            Viewed.add_user(engine, event.user_id, user['id'])
                    else:
                        self.message_send(event.user_id, 'Начинаем поиск')
                        self.users = self.api.search_users(self.params, self.offset)
                        while len(self.users) >= 1:
                            user = self.users.pop()
                            if Viewed.check_user(engine, event.user_id, user['id']):
                                continue
                            photos_user = self.api.get_photos(user['id'])
                            attachment = ''
                            for photo in photos_user:
                                attachment += f'photo{photo["owner_id"]}_{photo["id"]},'
                            self.message_send(event.user_id,
                                              f'Встречайте: {user["name"]}\nСсылка: vk.com/id{user["id"]}',
                                              attachment=attachment
                                             )
                            Viewed.add_user(engine, event.user_id, user['id'])
                        self.offset += 10

                elif command == 'пока':
                    self.message_send(event.user_id, 'Пока')
                else:
                    self.message_send(event.user_id, 'Команда не опознана')

    def ask_city(self, user_id):
        self.message_send(user_id, 'Укажите город, в котором ищем пару')
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                self.message_send(user_id, 'Записали, спасибо. Для поиска анкет введите: "Поиск"')
                return self.api.get_city(event.text)

    def ask_bdate(self, user_id):
        self.message_send(user_id, 'Укажите дату рождения в формате dd.mm.yyyy')
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                self.message_send(user_id, 'Записали, спасибо. Для поиска анкет введите: "Поиск"')
                return event.text


if __name__ == '__main__':
    bot = BotInterface(comunity_token, acces_token)
    bot.event_handler()
