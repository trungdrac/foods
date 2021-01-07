import random
from datetime import datetime
import json
import pickle

from faker import Faker

REAL_DISHES_DATA = 'real_dishes.pkl'
POOL_DATA = 'pool.pkl'

ADMINS = 20
USERS = 30
DISHES = 200

ADMIN_RANGE = (1, 1 + ADMINS)
USER_RANGE = (1 + ADMINS, 1 + ADMINS + USERS)
ALL_USERS = ADMINS + USERS
ALL_USER_RANGE = (1, 1 + ALL_USERS)

MODEL = 'model'
PK = 'pk'
FIELDS = 'fields'
AUTH_USER = 'auth.user'
FOODS_USER = 'foods.user'
FOODS_DISH = 'foods.dish'
FOODS_RATING = 'foods.rating'
HASHED_PASSWORD = 'pbkdf2_sha256$216000$E7eK2AnWdjH7$vA0IUnEP2MzszO+Ubxp00DSiXq2AbT6wBDMex3XU00I='
DATE_JOINED = '2020-12-23T14:49:21Z'
BIRTHDAY = '2000-01-01'

fake = Faker()
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def randlist(array):
    return array[random.randrange(0, len(array))]


def get_ingredients(pool, number, is_vn):
    rs = []
    if is_vn:
        for _ in range(number):
            rs.append(randlist(pool['ing']))
    else:
        for _ in range(number):
            rs.append(randlist(pool['en']))
    return tuple(rs)


def get_vn_dish(pool):
    return '{} {}'.format(
        randlist(pool['vn-1']),
        randlist(pool['vn-2'])
    )


def get_en_dish(pool):
    return '{0} {0}'.format(randlist(pool['en']))


def seed_user():
    auth_users = []
    foods_users = []
    for i in range(*ADMIN_RANGE):
        gender = fake.pybool()
        auth_admin = {
            'password': HASHED_PASSWORD,
            'last_login': None,
            'is_superuser': True,
            'username': 'admin_{}'.format(i),
            'first_name': fake.first_name_male() if gender else fake.first_name_female(),
            'last_name': fake.last_name_male() if gender else fake.last_name_female(),
            'email': fake.email(),
            'is_staff': True,
            'is_active': True,
            'date_joined': DATE_JOINED,
            'groups': (),
            'user_permissions': ()
        }
        foods_admin = {
            'user': i,
            'birthday': BIRTHDAY,
            'height': fake.pyint(min_value=101, max_value=250),
            'weight': fake.pyint(min_value=20, max_value=200),
            'gender': gender,
            'diet_factor': 1
        }
        auth_users.append({
            MODEL: AUTH_USER,
            PK: i,
            FIELDS: auth_admin
        })
        foods_users.append({
            MODEL: FOODS_USER,
            PK: i,
            FIELDS: foods_admin
        })
    for i in range(*USER_RANGE):
        gender = fake.pybool()
        auth_user = {
            'password': HASHED_PASSWORD,
            'last_login': None,
            'is_superuser': False,
            'username': 'user_{}'.format(i),
            'first_name': fake.first_name_male() if gender else fake.first_name_female(),
            'last_name': fake.last_name_male() if gender else fake.last_name_female(),
            'email': fake.email(),
            'is_staff': False,
            'is_active': True,
            'date_joined': DATE_JOINED,
            'groups': (),
            'user_permissions': ()
        }
        foods_user = {
            'user': i,
            'birthday': BIRTHDAY,
            'height': fake.pyint(min_value=100, max_value=250),
            'weight': fake.pyint(min_value=20, max_value=200),
            'gender': gender,
            'diet_factor': 1
        }
        auth_users.append({
            MODEL: AUTH_USER,
            PK: i,
            FIELDS: auth_user
        })
        foods_users.append({
            MODEL: FOODS_USER,
            PK: i,
            FIELDS: foods_user
        })
    return auth_users + foods_users


def seed_food_dish(real_dishes, pool):
    rs = []
    count = real_dishes
    dish_range = (1, 1+DISHES)
    for u in range(*ALL_USER_RANGE):
        for i in range(*dish_range):
            count += 1
            is_vn = fake.pybool()
            ingredients = get_ingredients(pool, random.randint(5, 15), is_vn)
            d = {
                'user': u,
                'dish_name': get_vn_dish(pool) if is_vn else get_en_dish(pool),
                'description': fake.text(50),
                'calories': random.randint(10, 3000),
                'is_public': fake.pybool(),
                'ingredients': ','.join(ingredients),
                'created_at': timestamp,
                'updated_at': timestamp
            }
            rs.append({
                MODEL: FOODS_DISH,
                PK: count,
                FIELDS: d
            })
    return rs


def seed_food_rating(real_dishes):
    dish_range = (1, 1+real_dishes+DISHES)
    rs = []
    for _ in range(5):
        for i in range(*dish_range):
            r = {
                'user': random.randrange(*USER_RANGE),
                'dish': i,
                'score': random.randint(1, 5),
                'comment': fake.text(50),
                'created_at': timestamp,
                'updated_at': timestamp
            }
            rs.append({
                MODEL: FOODS_RATING,
                PK: i,
                FIELDS: r
            })
    return rs


def load_pickle(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)


def test_dish_data(filename):
    with open(filename, 'r') as f:
        a = json.load(f)
        b = [i['pk'] for i in a if i['model'] == 'foods.dish']
        c = set(b)
        print(len(c))

        for i in range(len(b)-1):
            if b[i]+1 != b[i+1]:
                print('Diff: {}-{}'.format(b[i], b[i+1]))


def generate_data():
    real_dishes = load_pickle(REAL_DISHES_DATA)
    pool = load_pickle(POOL_DATA)
    a = seed_user()
    a += real_dishes
    a += seed_food_dish(len(real_dishes), pool)
    a += seed_food_rating(len(real_dishes))
    with open('data.json', 'w') as file:
        json.dump(a, file)


if __name__ == '__main__':
    generate_data()
    test_dish_data('data.json')
