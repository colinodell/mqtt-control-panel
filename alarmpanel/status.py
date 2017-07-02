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
            self.ui.draw_text(self.message, self.rect, self.color)
