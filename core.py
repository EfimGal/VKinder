from datetime import datetime
from pprint import pprint
import vk_api
from vk_api.exceptions import ApiError
from config import acces_token


class VkTools():
    def __init__(self, acces_token):
        self.api = vk_api.VkApi(token=acces_token)

    def get_profile_info(self, user_id):

        try:
            info, = self.api.method('users.get',
                                    {'user_id': user_id,
                                     'fields': 'city,bdate,sex,relation,home_town'
                                     }
                                    )
        except ApiError as e:
            info = {}
            pprint(f'Ошибка на стороне VK: {e}')

        user_info = {'name': (info['first_name'] + ' ' + info['last_name']) if 'first_name' in info and 'last_name' in info else None,
                     'id': info.get('id'),
                     'bdate': info.get('bdate'),
                     'home_town': info.get('home_town'),
                     'sex': info.get('sex'),
                     'city': info.get('city')['id'] if info.get('city') is not None else None
                     }
        return user_info

    def search_users(self, params, offset):

        sex = 1 if params['sex'] == 2 else 2
        city = params['city']
        current_year = datetime.now().year
        user_year = int(params['bdate'].split('.')[2])
        age = current_year - user_year
        age_from = age - 5
        age_to = age + 5
        try:
            users = self.api.method('users.search',
                                    {'count': 10,
                                     'offset': offset,
                                     'age_from': age_from,
                                     'age_to': age_to,
                                     'sex': sex,
                                     'city': city,
                                     'status': 6,
                                     'is_closed': False
                                     }
                                    )
        except ApiError as e:
            users = []
            print(f'error = {e}')

        result = [{'id': user['id'],
                   'name': user['first_name'] + ' ' + user['last_name']
                  } for user in users['items'] if user['is_closed'] is False and len(self.get_photos(user['id'])) >= 1
                 ]

        return result

    def get_photos(self, user_id):
        try:
            photos = self.api.method('photos.get',
                                     {'user_id': user_id,
                                      'album_id': 'profile',
                                      'extended': 1
                                      }
                                     )
        except ApiError as e:
            photos = {}
            print(f'error = {e}')

        result = [{'owner_id': item['owner_id'],
                   'id': item['id'],
                   'likes': item['likes']['count'],
                   'comments': item['comments']['count']
                   } for item in photos['items']
                  ]

        result.sort(key=lambda x: x['likes'] + x['comments'] * 10, reverse=True)
        return result[:3]

    def get_city(self, q=''):
        try:
            city = self.api.method('database.getCities',
                                    {'q': q,
                                     'count': 1
                                     }
                                  )
        except ApiError as e:
            city = {}
            print(f'error = {e}')
        item = city.get('items')
        if item:
            return item[0].get('id')
        else:
            return None


if __name__ == '__main__':
    #bot = VkTools(acces_token)
    #params = bot.get_profile_info(195050304)
    #pprint(params)
    #user = bot.search_users(params)[0]
    #photo_resp = bot.get_photos(user['id'])
    #pprint(photo_resp)
    #print(bot.get_city('2345'))
    #print(bot.get_photos(users[2]['id']))