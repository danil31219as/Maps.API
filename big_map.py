import os
import sys
import pygame
import requests


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


x, y = map(float, input('Координаты: ').split())
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
            # следующий код
            update()
            screen.blit(pygame.image.load('map.png'), (0, 0))
            
    pygame.display.flip()
pygame.quit()
os.remove('map.png')
