import os
import sys
import pygame
import requests

z = 1


def update():
    map_request = f"http://static-maps.yandex.ru/1.x/"
    map_params = {
        'll': ','.join(list(map(str, [x, y]))),
        'spn': ','.join(list(map(str, [delta_x, delta_y]))),
        'l': 'map'
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

pygame.init()
screen = pygame.display.set_mode((600, 450))

update()
screen.blit(pygame.image.load('map.png'), (0, 0))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

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
                y = y + 1 if y <= 84 else -85
            elif keys[pygame.K_DOWN]:
                y = y - 1 if y >= -84 else 85
            elif keys[pygame.K_RIGHT]:
                x = x + 1 if x <= 84 else -85
            elif keys[pygame.K_LEFT]:
                x = x - 1 if x >= -84 else 85
            update()
            screen.blit(pygame.image.load('map.png'), (0, 0))

    pygame.display.flip()
pygame.quit()
os.remove('map.png')