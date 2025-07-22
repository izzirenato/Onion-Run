import pygame
from parse_config import HEIGHT, SPEED, FPS, ASSETS

"""
Parallax scrolling background system for the OnionRun game.
Implements multi-layered backgrounds with different scroll speeds for depth perception,
seamlessly looping to create infinite scrolling effect.
"""

class Background:
    def __init__(self, background_layers=None):
        self.layers = []

        if background_layers is None:
            background_layers = \
            [
                {
                    'image_path': ASSETS['IMAGES']['GAME_BG'],
                    'scroll_factor': 0.3
                },
                {
                    'image_path': ASSETS['IMAGES']['GAME_BG_FLOOR'],
                    'scroll_factor': 1.0
                }
            ]

        base_speed = SPEED
        for i, layer_info in enumerate(background_layers):
            # Preload and convert images
            image = pygame.image.load(layer_info['image_path']).convert_alpha()
            image_height = image.get_height()
            scroll_factor = layer_info.get('scroll_factor', 0.5 + (i * 0.3))

            layer = \
            {
                'image': image,
                'y1': 0,
                'y2': -image_height,
                'scroll_factor': scroll_factor,
                'base_speed': base_speed,
                'image_height': image_height,
                'scroll_speed': base_speed * scroll_factor  # Pre-calculate for performance
            }
            self.layers.append(layer)

        # Pre-sort layers by scroll factor once
        self.layers.sort(key = lambda x: x['scroll_factor'])


    # draws the two images of the background
    def draw(self, screen):
        for layer in self.layers:
            screen.blit(layer['image'], (0, layer['y1']))
            screen.blit(layer['image'], (0, layer['y2']))


    # updates the background images every frame
    def update(self, dt_seconds):
        # Skip tiny dt values for optimization
        if dt_seconds <= 0.001:
            return

        for layer in self.layers:
            # Use pre-calculated scroll speed
            scroll_amount = layer['scroll_speed'] * dt_seconds * FPS

            layer['y1'] += scroll_amount
            layer['y2'] += scroll_amount

            image_height = layer['image_height']

            # check when a layer is completely off the viewport
            if layer['y1'] >= HEIGHT:
                layer['y1'] = layer['y2'] - image_height

            if layer['y2'] >= HEIGHT:
                layer['y2'] = layer['y1'] - image_height

            # make sure there are no gaps - optimized calculation
            y_diff = layer['y1'] - layer['y2']
            if abs(y_diff) > image_height:
                if y_diff < 0:
                    layer['y2'] = layer['y1'] + image_height
                else:
                    layer['y1'] = layer['y2'] + image_height