# This file contains a simple physics demo
#
# Author: Josh McIntyre
#

import pygame

# Handle scale - feet -> pixels
class Scaler:

    def __init__(self, pixels_per_foot):
        self.pixels_per_foot = pixels_per_foot
    
    def scale(self, feet):
        return feet * self.pixels_per_foot
        
    def descale(self, pixels):
        return pixels // self.pixels_per_foot

# Simulation settings
PIXELS_PER_FOOT = 25
scaler = Scaler(PIXELS_PER_FOOT)

WINDOW_HEIGHT = scaler.scale(30)
WINDOW_WIDTH = scaler.scale(25)
CLIMBER_START_POS = [scaler.scale(4), scaler.scale(1)]
PROTECTION_POS = [scaler.scale(2), scaler.scale(4)]
DISTANCE_ABOVE = scaler.scale(3)
SLACK = scaler.scale(2)
ROPE = scaler.scale(30)
STRETCH_PCT = 10
STRETCH = ROPE * (STRETCH_PCT / 100)
TOTAL_FREEFALL = (DISTANCE_ABOVE * 2) + SLACK
TOTAL_FALL = (DISTANCE_ABOVE * 2) + SLACK + STRETCH

# Falling climber state
class Climber:

    def __init__(self):
        
        # Physics state
        self.position = CLIMBER_START_POS
        self.gravity = 0.5
        self.falling = False
        self.fell = False
        self.velocity = 0.0
        self.protection = Protection()
        
        # Draw 
        self.color = (0, 255, 0)
        self.radius = 10

    def fall_init(self):
        self.falling = True
        self.fell = False
        self.velocity = self.velocity + self.gravity
        self.decel = 5
        self.decel_rate = 0.2

    def fall_update(self):
        if self.falling:

            # Check if we hit the slack point, and start decelerating
            if self.position[1] >= self.protection.slack_point:
                self.stretching = True
                self.velocity = self.decel
                self.decel = self.decel - self.decel_rate
                self.position = [self.position[0], self.position[1] + self.velocity]
                
                if self.velocity <= 0.0 or self.position[1] >= self.protection.stop_point:
                    self.falling = False
                    self.fell = True
                return

            # If still falling, update the velocity
            self.velocity = self.velocity + self.gravity
            self.position = [self.position[0], self.position[1] + self.velocity]


class Protection:

    def __init__(self):
        
        # Physics state
        self.position = PROTECTION_POS
        self.distance_above = DISTANCE_ABOVE
        self.slack = SLACK
        self.stretch = STRETCH
        self.slack_point = self.position[1] + self.distance_above + self.slack
        self.stop_point = self.position[1] + self.distance_above + self.slack + self.stretch

        # Draw
        self.slack_position = [self.position[0], self.slack_point]
        self.color = (0, 0, 255)
        self.slack_color = (255, 0, 0)
        self.radius = 5

# Pygame display
class DisplayManager:

    def __init__(self):
        pygame.init()
        self.display = pygame.display.set_mode([WINDOW_WIDTH, WINDOW_HEIGHT])

    def draw_climb(self, climber):
        pygame.draw.circle(self.display, climber.color, climber.position, climber.radius)
        pygame.draw.circle(self.display, climber.protection.color, climber.protection.position, climber.protection.radius)
        pygame.draw.circle(self.display, climber.protection.slack_color, climber.protection.slack_position, climber.protection.radius)
 
    def draw_scale(self):
        font = pygame.font.SysFont(None, 24)
        for height in range(0, scaler.descale(WINDOW_HEIGHT)):
            if not (height % 5):
                height_str = str(scaler.descale(WINDOW_HEIGHT) - height)
            else:
                height_str = "-"
            img = font.render(height_str, True, (0, 0, 0))
            pos = (scaler.scale(.5), scaler.scale(height))
            self.display.blit(img, pos)
            
    def draw_info(self, climber):
        font = pygame.font.SysFont(None, 24)
        h = scaler.descale(WINDOW_HEIGHT) - scaler.descale(CLIMBER_START_POS[1])
        info = f"Climber start height: {h}'"
        img = font.render(info, True, (0, 0, 0))
        pos = (250, 20)
        self.display.blit(img, pos)

        h = scaler.descale(DISTANCE_ABOVE)
        info = f"Distance above last protection: {h}'"
        img = font.render(info, True, (0, 0, 0))
        pos = (250, 35)
        self.display.blit(img, pos)

        h = scaler.descale(SLACK)
        info = f"Slack in system: {h}"
        img = font.render(info, True, (0, 0, 0))
        pos = (250, 50)
        self.display.blit(img, pos)
        
        h = scaler.descale(ROPE)
        info = f"Rope in system: {h}'"
        img = font.render(info, True, (0, 0, 0))
        pos = (250, 65)
        self.display.blit(img, pos)
        
        h = scaler.descale(STRETCH)
        info = f"Rope stretch: {h}'"
        img = font.render(info, True, (0, 0, 0))
        pos = (250, 80)
        self.display.blit(img, pos)
        
        if climber.fell:
            h = scaler.descale(TOTAL_FREEFALL)
            info = f"Total freefall distance: {h}'"
            img = font.render(info, True, (0, 0, 0))
            pos = (250, 150)
            self.display.blit(img, pos)

            h = scaler.descale(TOTAL_FALL)
            info = f"Total fall distance: {h}'"
            img = font.render(info, True, (0, 0, 0))
            pos = (250, 165)
            self.display.blit(img, pos)

    def draw(self, climber):
        self.display.fill((255, 255, 255))
        self.draw_climb(climber)
        self.draw_scale()
        self.draw_info(climber)
        pygame.display.flip()

# Pygame input
class InputManager:

    def __init__(self):
        self.quit = False
        self.reset = False

    def handle_input(self, climber):
        for event in pygame.event.get():
            
            # Quit events
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    self.quit = True
            if event.type == pygame.QUIT:
                pygame.quit()
                self.quit = True

            # Fall events
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:

                    # If the climber already fell, reset
                    if climber.fell:
                        self.reset = True
                        return

                    # Otherwise, initiate the fall
                    climber.fall_init()
                    self.reset = False

            # Reset events
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.reset = True

# The main entry point for the program
def main():

    # Setup
    display_mgr = DisplayManager()
    input_mgr = InputManager()
    clock = pygame.time.Clock()

    climber = Climber()

    # The main loop
    while not input_mgr.quit:

        # Draw 
        display_mgr.draw(climber)

        # Input
        input_mgr.handle_input(climber)
        if input_mgr.quit:
            break
        if input_mgr.reset:
            climber = Climber()

        # Update the climber state
        climber.fall_update()

        # Tick limit
        clock.tick(60)
    
if __name__ == "__main__":
    main()
