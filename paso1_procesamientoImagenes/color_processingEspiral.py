import numpy as np
from PIL import Image
import colorsys
import math


class ColorExtractorEspiral:
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
        # Convertir H, S, L a rangos 0-360, 0-100, 0-100
        return h * 360, s * 100, l * 100

    def extract_main_color(self):
        """Extrae el color principal en formato HSL."""
        hue_counts = {}
        main_color = None
        main_hue = None

        try:
            # Cambiar el bucle para que itere sobre las filas intermitentemente (cada fila sí, fila no)
            for i, row in enumerate(self.pixels):
                if i % 2 == 0:  # Evaluar solo filas pares
                    for j, pixel in enumerate(row):
                        if j % 2 == 0:  # Evaluar solo columnas pares
                            hsl = self._rgb_to_hsl(pixel)
                            # Agrupar en segmentos de 10 grados
                            hue = round(hsl[0] // 10) * 10
                            hue_counts[hue] = hue_counts.get(hue, 0) + 1

                            if main_hue is None or hue_counts[hue] > hue_counts.get(main_hue, 0):
                                main_hue = hue
                                main_color = hsl

            return tuple(main_color) if main_color is not None else None

        except Exception as e:
            print(f"Error durante la extracción de color en la imagen: {e}")
            raise e

    def extract_visual_hierarchy_colors(self, points):
        """Extrae hasta 6 colores utilizando los puntos calculados de la jerarquía visual."""
        colors = []

        for i, (x, y) in enumerate(points):
            color = self.pixels[y, x]
            hsl = self._rgb_to_hsl(color)

            if i == 0:
                colors.append(tuple(hsl))
            else:
                current_hue = hsl[0]  # Hue del color actual
                # Si la diferencia de tonos no es suficientemente grande, busca un color alternativo
                if all(abs(current_hue - c[0]) >= 5 for c in colors):
                    colors.append(tuple(hsl))
                else:
                    # Búsqueda de color alternativo si la diferencia no es >= 5
                    contadorBreak = 0
                    while len(colors) < 6:
                        # Derecha, Izquierda, Abajo, Arriba
                        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

                        for dx, dy in directions:
                            new_x = x + int(self.width * 0.1) * dx
                            new_y = y + int(self.height * 0.1) * dy

                            if 0 <= new_x < self.width and 0 <= new_y < self.height:
                                new_color = self.pixels[new_y, new_x]
                                new_hsl = self._rgb_to_hsl(new_color)
                                new_hue = new_hsl[0]

                                # Si el nuevo color tiene una diferencia de tono >= 10, se agrega
                                if all(abs(new_hue - c[0]) >= 10 for c in colors):
                                    colors.append(tuple(new_hsl))
                                    if len(colors) >= 6:
                                        break
                        if len(colors) >= 6:
                            break

                        # Aumenta el contador de intentos, si llega a 4, se detiene la búsqueda
                        contadorBreak += 1
                        if contadorBreak >= 4:
                            break

            # Si ya se han encontrado 6 colores, termina el ciclo principal
            if len(colors) >= 6:
                break
        # Oportunidad de obtener colores para completar la paleta de 6
        contadorBreak = 0
        while len(colors) < 6:
            for x, y in points:
                directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # Derecha, Izquierda, Abajo, Arriba
                for dx, dy in directions:
                    new_x = x + int(self.width * 0.2) * dx
                    new_y = y + int(self.height * 0.2) * dy
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


class JerarquiaVisualEspiral:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def calculate_spiral_points(self, n_points=6):
        """Calcula los puntos a lo largo de una espiral áurea correctamente."""
        golden_ratio = (1 + math.sqrt(5)) / 2  # Proporción áurea
        points = []

        if self.width > self.height:  # Imagen horizontal
            center_x = (2 * self.width) // 3
            center_y = (2 * self.height) // 3
        else:  # Imagen vertical
            center_x = self.width // 2
            center_y = (2 * self.height) // 3

        side_length = min(self.width, self.height) / (golden_ratio ** 4)
        angle = 0

        for i in range(n_points):
            angle += math.pi / 2
            mid_x = int(center_x + (side_length / 2) * math.cos(angle))
            mid_y = int(center_y - (side_length / 2) * math.sin(angle))

            if 0 <= mid_x < self.width and 0 <= mid_y < self.height:
                points.append((mid_x, mid_y))

            side_length *= golden_ratio

        return points


class CalculodeResultadosEspiral:
    def __init__(self, hierarchy_colors, main_color):
        self.hierarchy_colors = hierarchy_colors
        self.main_color = main_color

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

        hue_color_principal, saturation_color_principal, brightness_color_principal = self.main_color

        return {
            "image_path": image_path,
            "hueColorPrincipal": hue_color_principal,
            "saturationColorPrincipal": saturation_color_principal,
            "brightnessColorPrincipal": brightness_color_principal,
            "num_colors": len(self.hierarchy_colors),
            "avg_hue_diff": avg_hue_diff,
            "avg_saturation": avg_saturation_diff,
            "avg_pure_saturation": avg_saturation_pure,
            "avg_lightness": avg_lightness_diff,
            "avg_pure_lightness": avg_lightness_pure
        }
