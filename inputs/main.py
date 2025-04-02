def vyprintuj():
    return 1
print(vyprintuj());





# import pygame
# from Block import *
# from Player import *
# import random
# pygame.init()
# clock = pygame.time.Clock() # pro FPS
# screen = pygame.display.set_mode((400, 600))

# # Vytvoření hráče
# player = Player(200, 560, "obrazky/spaceship.png", 80)

# # Vytvoření bloků
# all_block_list = pygame.sprite.Group()
# randomX = random.randint(25, 375)
# block = Block(randomX, 25, "obrazky/ground.png", 50)
# all_block_list.add(block)

# # user event
# ADD_BLOCK = pygame.USEREVENT + 1
# pygame.time.set_timer(ADD_BLOCK, 1000) # 1000 ms = 1s

# running = True
# while running: # vše co je zde měním dynamicky dle ticku
#     screen.fill((255, 255, 255))
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
#         if event.type == ADD_BLOCK:
#             randomX = random.randint(25, 375)
#             block = Block(randomX, 25, "obrazky/ground.png", 50)
#             all_block_list.add(block)
#     # Update vsech prvků
#     if pygame.sprite.spritecollide(player, all_block_list, False, pygame.sprite.collide_mask):
#         pygame.time.delay(5000)
#         running = False
#     all_block_list.update()
#     player.update()
#     # vykresleni vsech prvku
#     player.draw(screen)
#     all_block_list.draw(screen)
#     pygame.display.flip()
#     clock.tick(60) # FPS
# pygame.quit()
