import os
import sys
import pygame
import requests

Z = 0.003
l = "map"
pygame.init()
screen = pygame.display.set_mode((600, 450))


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


class chouse_bar:
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


def update(x, y):
    map_request = f"http://static-maps.yandex.ru/1.x/"
    map_params = {
        'll': ','.join([str(x), str(y)]),
        'spn': ','.join([str(delta_x), str(delta_y)]),
        'l': l,
        'pt': ','.join([str(x), str(y)]) + ',pm2blm'
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


x = y = delta_x = delta_y = 0
address = ''
screen.fill((0, 0, 0))
bar = chouse_bar()
map = False
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            map_r = bar.check(pygame.mouse.get_pos())
            if map_r:
                l = map_r
            update(x, y)
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
                    map = True
                    x, y = search
                    delta_x, delta_y = set_spn(address)
                    update(x, y)
                    screen.blit(pygame.image.load('map.png'), (0, 0))
            elif keys[pygame.K_BACKSPACE]:
                address = address[:-1]
            elif len(address) < 50:
                address += event.unicode
            if map:
                update(x, y)
                screen.blit(pygame.image.load('map.png'), (0, 0))
    pygame.draw.rect(screen, (255, 255, 255), ((0, 420), (300, 30)))
    font = pygame.font.Font(None, 20)
    text = font.render(str(address), 1, (0, 0, 0))
    screen.blit(text, (0, 430))
    bar.draw()
    pygame.display.flip()
pygame.quit()
os.remove('map.png')
