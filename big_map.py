import os
import sys
import pygame
import requests
import math

Z = 0.03
l = "map"
pygame.init()
screen = pygame.display.set_mode((600, 450))


def lonlat_distance(a, b):
    degree_to_meters_factor = 111 * 1000
    a_lon, a_lat = list(map(float, a))
    b_lon, b_lat = list(map(float, b))
    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)
    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor
    distance = math.sqrt(dx * dx + dy * dy)
    return distance


def search_object(a, b):
    a, b = map(str, [a, b])
    geocoder_request = f"""http://geocode-maps.yandex.ru/1.x/"""
    geocoder_params = {
        'apikey': '40d1649f-0493-4b70-98ba-98533de7710b',
        'geocode': ','.join([a, b]),
        'format': 'json'
    }
    response = requests.get(geocoder_request, params=geocoder_params)
    return \
        response.json()["response"]["GeoObjectCollection"]["featureMember"][0][
            "GeoObject"]["metaDataProperty"]["GeocoderMetaData"]["text"]


def get_name(address):
    geocoder_request = f"""http://geocode-maps.yandex.ru/1.x/"""
    geocoder_params = {
        'apikey': '40d1649f-0493-4b70-98ba-98533de7710b',
        'geocode': address,
        'format': 'json'
    }
    response = requests.get(geocoder_request, params=geocoder_params)
    if response:
        json_response = response.json()
        return \
            json_response['response']['GeoObjectCollection']['featureMember'][
                0][
                'GeoObject'][
                'metaDataProperty']['GeocoderMetaData']['text']


def get_index(address):
    geocoder_request = f"""http://geocode-maps.yandex.ru/1.x/"""
    geocoder_params = {
        'apikey': '40d1649f-0493-4b70-98ba-98533de7710b',
        'geocode': address,
        'format': 'json'
    }
    response = requests.get(geocoder_request, params=geocoder_params)
    if response:
        json_response = response.json()
        try:
            return \
                json_response["response"]["GeoObjectCollection"][
                    "featureMember"][0][
                    "GeoObject"]["metaDataProperty"]["GeocoderMetaData"][
                    'Address'][
                    'postal_code']
        except:
            return 'нет индекса'


def set_spn(toponym_to_find):
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": toponym_to_find,
        "format": "json"}
    response = requests.get(geocoder_api_server, params=geocoder_params)
    json_response = response.json()
    # Получаем первый топоним из ответа геокодера.
    toponym = json_response["response"]["GeoObjectCollection"][
        "featureMember"][0]["GeoObject"]
    toponym_s = toponym["boundedBy"]["Envelope"]
    x1, y1 = float(toponym_s["lowerCorner"].split()[0]), float(
        toponym_s["lowerCorner"].split()[1])
    x2, y2 = float(toponym_s["upperCorner"].split()[0]), float(
        toponym_s["upperCorner"].split()[1])
    return abs(x2 - x1), abs(y2 - y1)


def search_organiz(a, b, text):
    a, b = map(str, [a, b])
    search_api_server = "https://search-maps.yandex.ru/v1/"
    apikey_search = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
    search_params = {
        "apikey": apikey_search,
        "text": text,
        "lang": "ru_RU",
        'll': ','.join([a, b]),
        "type": "biz"
    }
    response_org = requests.get(search_api_server, params=search_params).json()
    organization = response_org["features"][0]
    point = organization["geometry"]["coordinates"]
    if lonlat_distance(point, (a, b)) <= 50000:
        return point, organization['properties']['description'], organization['properties']['name']


def get_coor(address):
    geocoder_request = f"""http://geocode-maps.yandex.ru/1.x/"""
    geocoder_params = {
        'apikey': '40d1649f-0493-4b70-98ba-98533de7710b',
        'geocode': address,
        'format': 'json'
    }
    response = requests.get(geocoder_request, params=geocoder_params)
    if response:
        json_response = response.json()
        toponym = \
            json_response["response"]["GeoObjectCollection"]["featureMember"][
                0][
                "GeoObject"]
        return [float(toponym["Point"]["pos"].split()[0]),
                float(toponym["Point"]["pos"].split()[1])]
    return False


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname)
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class clear_search:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.image = load_image("clear_search_btn.png")

    def check(self, coor):
        if coor[1] > 419 and coor[1] < 451 and coor[0] > 569 and coor[1] < 601:
            return True
        return False

    def draw(self):
        screen.blit(self.image, (570, 420))


class choose_bar:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.images = [load_image("shema.png"), load_image("sputnik.png"),
                       load_image("gibrid.png")]
        self.image = self.images[0]

    def check(self, coor):
        if coor[1] > 0 and coor[1] < 30:
            if coor[0] < 66:
                self.image = self.images[0]
                return "map"
            elif coor[0] < 133:
                self.image = self.images[1]
                return "sat"
            elif coor[0] < 200:
                self.image = self.images[2]
                return "sat,skl"
        return False

    def draw(self):
        screen.blit(self.image, (0, 0))


def update():
    map_request = f"http://static-maps.yandex.ru/1.x/"
    map_params = {
        'll': ','.join([str(x), str(y)]),
        'spn': ','.join([str(delta_x), str(delta_y)]),
        'l': l,
        'pt': "" if pt_x == "" and pt_y == "" else ','.join(
            [str(pt_x), str(pt_y)]) + ',pm2blm'
    }

    map_response = requests.get(map_request, params=map_params)

    if not map_response:
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", map_response.status_code, "(",
              map_response.reason, ")")
        sys.exit(1)

    map_file = "map.png"
    with open(map_file, "wb") as file:
        file.write(map_response.content)


class ChooseIndex:
    def __init__(self):
        self.x = 300
        self.y = 420
        self.i = 1
        self.images = [
            pygame.transform.scale(load_image("off.png", (255, 255, 255)),
                                   (50, 30)),
            pygame.transform.scale(load_image("on.png", (255, 255, 255)),
                                   (50, 30))]
        self.image = self.images[self.i % 2]

    def check(self, coor):
        if coor[0] > 300 and coor[0] < 350 and coor[1] > 420 and coor[1] < 450:
            self.i += 1
            self.image = self.images[self.i % 2]
            return True
        return False

    def draw(self):
        screen.blit(self.image, (self.x, self.y))


x = y = delta_x = delta_y = pt_x = pt_y = x0 = y0 = 0
address = ''
pt_x, pt_y = "", ""
data = ""
p_i = ""
screen.fill((0, 0, 0))
bar = choose_bar()
postal_index = ChooseIndex()
postal_bool = True
clear_btn = clear_search()
running = True
update()
screen.blit(pygame.image.load('map.png'), (0, 0))
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            map_r = bar.check(pygame.mouse.get_pos())
            check_clear = clear_btn.check(pygame.mouse.get_pos())
            postal_r = postal_index.check(pygame.mouse.get_pos())
            if map_r:
                l = map_r
            elif check_clear:
                pt_y, pt_x = "", ""
                data = ""
                p_i = ""
            elif postal_r:
                postal_bool = True if postal_bool == False else False
            else:
                if event.button == 1:
                    x0 = x - delta_x * 2 / 600 * 300
                    y0 = y + delta_y * 2 / 450 * 225
                    pt_x = pygame.mouse.get_pos()[0] * delta_x * 2 / 600 + x0
                    pt_y = y0 - (pygame.mouse.get_pos()[1] * delta_y * 2 / 450)
                    address = search_object(pt_x, pt_y)
                    p_i = get_index(address)
                    data = get_name(address)
                elif event.button == 3:
                    x0 = x - delta_x * 2 / 600 * 300
                    y0 = y + delta_y * 2 / 450 * 225
                    pt_x = pygame.mouse.get_pos()[0] * delta_x * 2 / 600 + x0
                    pt_y = y0 - (pygame.mouse.get_pos()[1] * delta_y * 2 / 450)
                    tmp, address, name = search_organiz(pt_x, pt_y, address)
                    pt_x, pt_y = tmp
                    p_i = get_index(address)
                    data = name
            update()
            screen.blit(pygame.image.load('map.png'), (0, 0))
        if event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_PAGEUP]:
                delta_x *= 2
                delta_y *= 2
                if delta_y > 100 or delta_x > 100:
                    delta_y = 0.001953125
                    delta_x = 0.001953125
            elif keys[pygame.K_PAGEDOWN]:
                delta_x /= 2
                delta_y /= 2
                if delta_y < 0.001953125 or delta_x < 0.001953125:
                    delta_y = 90
                    delta_x = 90
            if keys[pygame.K_UP]:
                y = y + Z if y <= 84 else -85
            elif keys[pygame.K_DOWN]:
                y = y - Z if y >= -84 else 85
            elif keys[pygame.K_RIGHT]:
                x = x + Z if x <= 84 else -85
            elif keys[pygame.K_LEFT]:
                x = x - Z if x >= -84 else 85
            keys = pygame.key.get_pressed()
            if keys[13]:
                search = get_coor(address)
                if search:
                    x, y = search
                    pt_x, pt_y = search
                    p_i = get_index(address)
                    data = get_name(address)
                    delta_x, delta_y = set_spn(address)
                    update()
                    screen.blit(pygame.image.load('map.png'), (0, 0))
            elif keys[pygame.K_BACKSPACE]:
                address = address[:-1]
            elif len(address) < 50:
                address += event.unicode
            update()
            screen.blit(pygame.image.load('map.png'), (0, 0))
    pygame.draw.rect(screen, (255, 255, 255), ((0, 420), (300, 30)))
    pygame.draw.rect(screen, (255, 255, 255), ((200, 0), (400, 30)))
    pygame.draw.rect(screen, (255, 255, 255), ((350, 420), (100, 30)))
    font = pygame.font.Font(None, 20)
    text = font.render(str(address), 1, (0, 0, 0))
    text_adress = font.render(str(data), 1, (0, 0, 0))
    text_index = font.render(str(p_i), 1, (0, 0, 0))
    screen.blit(text, (0, 430))
    screen.blit(text_adress, (200, 10))
    if postal_bool:
        screen.blit(text_index, (350, 430))
    bar.draw()
    postal_index.draw()
    clear_btn.draw()
    pygame.display.flip()
pygame.quit()
os.remove('map.png')
