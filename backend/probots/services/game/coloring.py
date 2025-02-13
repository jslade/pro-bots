import random

from ...models.game.all import ColorScheme


class ColoringService:
    def generate_random(self, theme: str) -> ColorScheme:
        if theme not in ["light", "dark"]:
            raise ValueError("Theme must be 'light' or 'dark'")

        body_color = self._generate_body_color(theme)
        head_color, tail_color = self._generate_complementary_colors(theme)

        return ColorScheme(body=body_color, head=head_color, tail=tail_color)

    def _generate_body_color(self, theme: str) -> str:
        if theme == "light":
            base_color = 150
        else:
            base_color = 50

        return self.color_from_base(base_color)

    def _generate_complementary_colors(self, theme: str) -> tuple:
        if theme == "light":
            head_base = random.randint(150, 200)
            tail_base = 255 - int(head_base / 2)
        else:
            head_base = random.randint(50, 100)
            tail_base = 255 - head_base

        head_color = self.color_from_base(head_base)
        tail_color = self.color_from_base(tail_base)

        return head_color, tail_color

    def rgb_from_base(self, base: int, variation: int = 40) -> tuple[int, int, int]:
        dr = random.randint(-variation, variation)
        dg = random.randint(-variation, variation)
        db = random.randint(-variation, variation)

        r = max(0, min(255, base + dr))
        g = max(0, min(255, base + dg))
        b = max(0, min(255, base + db))
        return (r, g, b)

    def color_from_base(self, base: int, variation: int = 40) -> tuple[int, int, int]:
        r, g, b = self.rgb_from_base(base)
        return f"#{r:02x}{g:02x}{b:02x}"
