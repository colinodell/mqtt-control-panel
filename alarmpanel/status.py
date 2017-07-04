class StatusLine:
    def __init__(self, ui, rect, color):
        self.ui = ui
        self.rect = rect
        self.color = color
        self.message = ''

    def set(self, message):
        if self.message != message:
            self.message = message

            # Draw the label
            self.draw()

    def draw(self):
        # Redraw the background area behind the text
        self.ui.blit_background(self.rect)

        # Draw the label
        label = self.ui.render_text(self.message, self.color)
        self.ui.blit(label, self.rect)
