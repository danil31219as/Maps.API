import os
import sys
import pygame
import requests

z = 1
l = "map"
pygame.init()
screen = pygame.display.set_mode((600, 450))


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
        self.images = [load_image("shema.png"), load_image("sputnik.png"), load_image("gibrid.png")]
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
        'll': ','.join(list(map(str, [x, y]))),
        'spn': ','.join(list(map(str, [delta_x, delta_y]))),
        'l': l
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


y, x = map(float, input('Координаты: ').split())
delta_x, delta_y = map(float, input('Масштаб: ').split())

update()
screen.blit(pygame.image.load('map.png'), (0, 0))
bar = chouse_bar()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            map_r = bar.check(pygame.mouse.get_pos())
            if map_r:
                l = map_r
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
                y = y + 0.3 if y <= 84 else -85
            elif keys[pygame.K_DOWN]:
                y = y - 0.3 if y >= -84 else 85
            elif keys[pygame.K_RIGHT]:
                x = x + 0.3 if x <= 84 else -85
            elif keys[pygame.K_LEFT]:
                x = x - 0.3 if x >= -84 else 85
            update()
            screen.blit(pygame.image.load('map.png'), (0, 0))
    bar.draw()
    pygame.display.flip()
pygame.quit()
os.remove('map.png')
