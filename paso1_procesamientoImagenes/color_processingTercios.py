import numpy as np
from PIL import Image
import colorsys


class ColorExtractorTercios:
    def __init__(self, image_path):
        try:
            self.image = Image.open(image_path)
            self.pixels = np.array(self.image)
            self.height, self.width, _ = self.pixels.shape
        except Exception as e:
            print(f"Error al abrir la imagen {image_path}: {e}")
            raise e

    def _rgb_to_hsl(self, rgb):
        r, g, b = rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        return h * 360, s * 100, l * 100

    def extract_visual_hierarchy_colors(self, points):
        """Extrae hasta 6 colores utilizando los puntos calculados de la jerarquía visual."""
        colors = []

        for i, (x, y) in enumerate(points):
            color = self.pixels[y, x]
            hsl = self._rgb_to_hsl(color)

            if i == 0:
                colors.append(tuple(hsl))
            else:
                last_hue = colors[-1][0]
                current_hue = hsl[0]

                if abs(current_hue - last_hue) >= 5:
                    colors.append(tuple(hsl))

        # Obtener colores adicionales con un ciclo while
        contadorBreak = 0
        while len(colors) < 6:
            for x, y in points:
                directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # Derecha, Izquierda, Abajo, Arriba
                for dx, dy in directions:
                    new_x = x + int(self.width * 0.1) * dx
                    new_y = y + int(self.height * 0.1) * dy
                    if 0 <= new_x < self.width and 0 <= new_y < self.height:
                        new_color = self.pixels[new_y, new_x]
                        new_hsl = self._rgb_to_hsl(new_color)
                        if all(abs(new_hsl[0] - c[0]) >= 10 for c in colors):
                            colors.append(tuple(new_hsl))
                            if len(colors) >= 6:
                                break
                if len(colors) >= 6:
                    break
                contadorBreak += 1
            if contadorBreak >= 4:
                break

        return colors


class JerarquiaVisualTercios:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def calculate_rule_of_thirds_points(self):
        """Calcula los 4 puntos de intersección en una cuadrícula de 3x3 (regla de tercios)."""
        points = []

        # Dividir la imagen en tercios
        third_x = self.width // 3
        third_y = self.height // 3

        # Puntos de intersección de la cuadrícula de tercios
        points.append((third_x, third_y))
        points.append((2 * third_x, third_y))
        points.append((third_x, 2 * third_y))
        points.append((2 * third_x, 2 * third_y))

        return points


class CalculodeResultadosTercios:
    def __init__(self, hierarchy_colors):
        self.hierarchy_colors = hierarchy_colors

    def calcular_promedios(self, image_path):
        hues = [color[0] for color in self.hierarchy_colors]
        saturations = [color[1] for color in self.hierarchy_colors]
        lightness = [color[2] for color in self.hierarchy_colors]

        if len(hues) > 1:
            avg_hue_diff = sum(abs(hues[i] - hues[i - 1])
                               for i in range(1, len(hues))) / (len(hues) - 1)
        else:
            avg_hue_diff = 0

        sat_range = max(saturations) - min(saturations)
        if sat_range < 20:
            avg_saturation_pure = sum(saturations) / len(saturations)
            avg_saturation_diff = None
        else:
            avg_saturation_diff = sum(abs(saturations[i] - saturations[i - 1])
                                      for i in range(1, len(saturations))) / (len(saturations) - 1)
            avg_saturation_pure = None

        light_range = max(lightness) - min(lightness)
        if light_range < 20:
            avg_lightness_pure = sum(lightness) / len(lightness)
            avg_lightness_diff = None
        else:
            avg_lightness_diff = sum(abs(lightness[i] - lightness[i - 1])
                                     for i in range(1, len(lightness))) / (len(lightness) - 1)
            avg_lightness_pure = None
        return {
            "image_path": image_path,
            "num_colors": len(self.hierarchy_colors),
            "avg_hue_diff": avg_hue_diff,
            "avg_saturation": avg_saturation_diff,
            "avg_pure_saturation": avg_saturation_pure,
            "avg_lightness": avg_lightness_diff,
            "avg_pure_lightness": avg_lightness_pure
        }