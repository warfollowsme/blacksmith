import pygame
from constants import (
    WIDTH, font, WHITE, BLACK, DARK_GRAY, pygame
)
from textwrap import wrap

notifications = []

class Notification:
    def __init__(self, message):
        self.width = int(WIDTH * 0.25)  # 25% of screen width
        self.height = 50
        self.rect = pygame.Rect(
            (WIDTH - self.width) // 2,  # Center horizontally
            -self.height,  # Start above the screen for slide-down animation
            self.width,
            self.height
        )
        self.target_y = 20  # Position slightly below the top edge
        self.alpha = 255
        self.start_time = pygame.time.get_ticks()
        self.duration = 10000  # 10 seconds
        self.close_button_size = 10  # Reduced size
        self.close_button_rect = pygame.Rect(
            self.rect.x + self.width - self.close_button_size - 10,  # 10 px padding from the right edge
            self.rect.y + (self.height - self.close_button_size) // 2,  # Center vertically
            self.close_button_size,
            self.close_button_size
        )
        self.animation_speed = 200  # Pixels per second
        self.message = message
        # Prepare text wrapping
        self.text_lines = self.wrap_text(message, self.width - 20 - self.close_button_size)

        # Adjust height based on number of lines
        self.line_height = font.get_linesize()
        self.height = max(50, 20 + len(self.text_lines) * self.line_height)
        self.rect.height = self.height
        self.rect.y = -self.height  # Reset y position based on new height
        self.close_button_rect.y = self.rect.y + (self.height - self.close_button_size) // 2

    def wrap_text(self, text, max_width):
        words = text.split(' ')
        lines = []
        current_line = ''
        for word in words:
            test_line = current_line + ' ' + word if current_line else word
            text_width, _ = font.size(test_line)
            if text_width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines

    def update(self, dt):
        # Update vertical position for slide-down animation
        if self.rect.y < self.target_y:
            self.rect.y += self.animation_speed * dt
            if self.rect.y > self.target_y:
                self.rect.y = self.target_y
            self.close_button_rect.y = self.rect.y + (self.height - self.close_button_size) // 2

        # Fade out after duration
        elapsed_time = pygame.time.get_ticks() - self.start_time
        if elapsed_time > self.duration:
            self.alpha -= 5  # Adjust fade speed as needed
            if self.alpha <= 0:
                return False  # Remove notification
        return True

    def draw(self, surface):
        notification_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        notification_surf.set_alpha(self.alpha)
        # Draw rounded rectangle
        pygame.draw.rect(notification_surf, DARK_GRAY, notification_surf.get_rect(), border_radius=10)
        # Draw message
        y_offset = 10
        for line in self.text_lines:
            text = font.render(line, True, WHITE)
            text_rect = text.get_rect()
            text_rect.x = 10
            text_rect.y = y_offset
            notification_surf.blit(text, text_rect)
            y_offset += self.line_height
        # Draw close button ('X' in black with no background)
        x_offset = self.close_button_rect.x - self.rect.x
        y_offset = self.close_button_rect.y - self.rect.y
        x1, y1 = x_offset, y_offset
        x2, y2 = x_offset + self.close_button_size, y_offset + self.close_button_size
        # Draw 'X' lines (smaller size)
        pygame.draw.line(notification_surf, BLACK, (x1, y1), (x2, y2), 2)
        pygame.draw.line(notification_surf, BLACK, (x1, y2), (x2, y1), 2)
        # Blit to main surface
        surface.blit(notification_surf, (self.rect.x, self.rect.y))

    def is_clicked(self, mouse_pos):
        return self.close_button_rect.collidepoint(mouse_pos)

def add_notification(message):
    # Clear any existing notifications
    notifications.clear()
    # Add the new notification
    notifications.append(Notification(message))