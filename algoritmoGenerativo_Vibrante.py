import csv
import random
import colorsys

class Probabilidades:
    def __init__(self):
        self.cantidad_colores = []
        self.hue_principal = []
        self.saturation_principal = []
        self.brightness_principal = []
        self.hue_diferencia = []
        self.saturation_diferencia = []
        self.brightness_diferencia = []


class ObtenerProbabilidad_ColorPrincipal:
    def __init__(self, archivo_csv):
        self.archivo_csv = archivo_csv
        self.probabilidades = Probabilidades()

    def cargar(self):
        with open(self.archivo_csv, mode='r') as file:
            reader = list(csv.DictReader(file))

            # Divisiones de filas según las reglas
            filas_hue = 36
            filas_saturation = 10
            
            # Procesar cada fila una vez
            for idx, row in enumerate(reader):
                row = {key.strip(): value for key, value in row.items()}

                # Procesar saturación y brillo
                if idx < filas_saturation:
                    self._procesar_saturation_brightness_principal(row)
                    self._procesar_hue_principal(row)
                # Procesar hue
                elif idx < filas_hue:
                    self._procesar_hue_principal(row)

    def _procesar_hue_principal(self, row):
        hue_min = float(row["hue_min"])
        hue_max = float(row["hue_max"])
        hue_prob = float(row["hue_probabilidad"])
        self.probabilidades.hue_principal.append((hue_min, hue_max, hue_prob))

    def _procesar_saturation_brightness_principal(self, row):
        saturation_min = float(row["saturation_min"])
        saturation_max = float(row["saturation_max"])
        saturation_prob = float(row["saturation_probabilidad"])
        brightness_min = float(row["brightness_min"])  
        brightness_max = float(row["brightness_max"])  
        brightness_prob = float(row["brightness_probabilidad"])
        self.probabilidades.saturation_principal.append((saturation_min, saturation_max, saturation_prob))
        self.probabilidades.brightness_principal.append((brightness_min, brightness_max, brightness_prob))

class ObtenerProbabilidad_Diferencial:
    def __init__(self, archivo_csv):
        self.archivo_csv = archivo_csv
        self.probabilidades = {
            "diagonal": Probabilidades(),
            "espiral": Probabilidades(),
            "simetria": Probabilidades(),
            "tercios": Probabilidades()
        }

    def cargar(self):
        with open(self.archivo_csv, mode='r') as file:
            reader = list(csv.DictReader(file))
             # Divisiones de filas según las reglas
            filas_cantidad_colores = 5
            filas_hue = 36
            filas_saturation=10

        # Procesar cada fila una vez
            for idx, row in enumerate(reader):
                row = {key.strip(): value for key, value in row.items()}

                # Procesar cantidad de colores
                if idx < filas_cantidad_colores:
                    self._procesar_cantidad_colores(row)
                    self._procesar_saturation_brightness_diferencias(row)
                    self._procesar_hue_diferencias(row)
                                # Procesar saturación y brillo
                elif idx < filas_saturation:
                    self._procesar_saturation_brightness_diferencias(row)
                    self._procesar_hue_diferencias(row)
                # Procesar hue
                elif idx < filas_hue:
                    self._procesar_hue_diferencias(row)

    def _procesar_cantidad_colores(self, row):
        for jerarquia in self.probabilidades:
            cantidad = int(row[f"cantidad_{jerarquia}"])
            probabilidad = float(row[f"cantidad_probabilidad_{jerarquia}"])
            self.probabilidades[jerarquia].cantidad_colores.append((cantidad, probabilidad))

    def _procesar_hue_diferencias(self, row):
        for jerarquia in self.probabilidades:
            hue_min = float(row[f"hue_min_{jerarquia}"])
            hue_max = float(row[f"hue_max_{jerarquia}"])
            hue_probabilidad = float(row[f"hue_probabilidad_{jerarquia}"])
            self.probabilidades[jerarquia].hue_diferencia.append((hue_min, hue_max, hue_probabilidad))

    def _procesar_saturation_brightness_diferencias(self, row):
        for jerarquia in self.probabilidades:
            saturation_min = float(row[f"saturation_min_{jerarquia}"])
            saturation_max = float(row[f"saturation_max_{jerarquia}"])
            saturation_prob = float(row[f"saturation_probabilidad_{jerarquia}"])
            brightness_min = float(row[f"brightness_min_{jerarquia}"])
            brightness_max = float(row[f"brightness_max_{jerarquia}"])
            brightness_prob = float(row[f"brightness_probabilidad_{jerarquia}"])
            self.probabilidades[jerarquia].saturation_diferencia.append((saturation_min, saturation_max, saturation_prob))
            self.probabilidades[jerarquia].brightness_diferencia.append((brightness_min, brightness_max, brightness_prob))

class GeneradorVibrantPalette:
    def __init__(self, archivo_csv_principal, archivo_csv_diferencial, color_principal=None, tipo_paleta='Calida'):
        self.cargador_color_principal = ObtenerProbabilidad_ColorPrincipal(archivo_csv_principal)
        self.cargador_color_principal.cargar()

        self.cargador_diferencial = ObtenerProbabilidad_Diferencial(archivo_csv_diferencial)
        self.cargador_diferencial.cargar()

        self.color_principal = color_principal
        self.tipo_paleta = tipo_paleta
        self.colores_hsl = []

    def _seleccionar_por_probabilidad(self, tipo_probabilidad):
        
        valores = []
        probabilidades = []
        for item in tipo_probabilidad:
            if len(item) == 2:  # Caso de tupla con (cantidad, probabilidad)
                valores.append(item[0])  
                probabilidades.append(item[1]) 
            elif len(item) == 3:  # Caso de tupla con (min, max, probabilidad)
                valores.append(random.uniform(item[0], item[1]))  # Generar un valor aleatorio entre min y max
                probabilidades.append(item[2]) 
            #else:
            #    raise ValueError("Formato inesperado en la tupla: se esperaba longitud 2 o 3.")
        
        print("Valores:", valores)
        print("Probabilidades:", probabilidades)
        # Elegir un valor basado en las probabilidades
        valor_finalPaleta = random.choices(valores, weights=probabilidades)[0]
        print("Valor seleccionado para Paleta Generativa:", valor_finalPaleta)  # línea para depuración
        return valor_finalPaleta

    def _generar_color_principal(self):
        hue = self._seleccionar_por_probabilidad(self.cargador_color_principal.probabilidades.hue_principal)
        saturation = self._seleccionar_por_probabilidad(self.cargador_color_principal.probabilidades.saturation_principal)
        brightness = self._seleccionar_por_probabilidad(self.cargador_color_principal.probabilidades.brightness_principal)
        return (hue, saturation, brightness)
    
    # Dirección de ajuste de saturación o briloo (aumentar, disminuir o aleatorio)
    def ajustar_direccion(self,total_diferencia):
        if total_diferencia < 10:
            return 1  # Aumentar
        elif total_diferencia > 90:
            return -1  # Disminuir
        else:
            return random.choice([-1, 1])  # Aleatorio
    def _hsl_to_rgb(self, h, s, l):
        r, g, b = colorsys.hls_to_rgb(h / 360, l / 100, s / 100)
        return int(r * 255), int(g * 255), int(b * 255)

    def generar_paleta(self):
        # Generación de color principal
        if not self.color_principal:
            color_hsl_principal = self._generar_color_principal()
        else:
            r, g, b = [x / 255.0 for x in self.color_principal]
            h, l, s = colorsys.rgb_to_hls(r, g, b)
            color_hsl_principal = (h * 360, s * 100, l * 100)

        # Selección de jerarquía de colores
        jerarquias = ['diagonal', 'espiral', 'simetria', 'tercios']
        probabilidades = [0.28, 0.26, 0.24, 0.22]
        jerarquia = random.choices(jerarquias, weights=probabilidades, k=1)[0]

        # Cargar las probabilidades para la jerarquía
        cantidad_colores = self._seleccionar_por_probabilidad(self.cargador_diferencial.probabilidades[jerarquia].cantidad_colores)
        diferencia_tono = self._seleccionar_por_probabilidad(self.cargador_diferencial.probabilidades[jerarquia].hue_diferencia)
        total_saturacion = self._seleccionar_por_probabilidad(self.cargador_diferencial.probabilidades[jerarquia].saturation_diferencia)
        total_brightness = self._seleccionar_por_probabilidad(self.cargador_diferencial.probabilidades[jerarquia].brightness_diferencia)

        # Ajustar dirección de saturación y brillo
        direccion_saturacion = self.ajustar_direccion(color_hsl_principal[1])
        direccion_brightness = self.ajustar_direccion(color_hsl_principal[2])

        colores_validos = []  # Lista de colores generados

        for i in range(1, cantidad_colores + 1):
            if self.tipo_paleta == 'Calida':
                nuevo_hue = (color_hsl_principal[0] - diferencia_tono * i) % 360
            else:
                nuevo_hue = (color_hsl_principal[0] + diferencia_tono * i) % 360

            # Calcular nueva saturación y brillo, asegurándose de que no sean demasiado bajos
            nuevo_saturation = max(20, min(100, color_hsl_principal[1] + (direccion_saturacion * total_saturacion * (i + 1) / (cantidad_colores))))
            nuevo_brightness = max(40, min(100, color_hsl_principal[2] + (direccion_brightness * total_brightness * (i + 1) / (cantidad_colores))))

            nuevo_color = (nuevo_hue, nuevo_saturation, nuevo_brightness)

            # Validar si el color es único
            es_valido = True
            for color_anterior in colores_validos:
                hue_anterior, saturation_anterior, brightness_anterior = color_anterior
                hueCondition = abs(nuevo_hue - hue_anterior) < 10
                saturationCondition = abs(nuevo_saturation - saturation_anterior) < 10
                brightnessCondition = abs(nuevo_brightness - brightness_anterior) < 5

                if hueCondition or saturationCondition or brightnessCondition:
                    es_valido = False
                    break

            if es_valido:
                colores_validos.append(nuevo_color)
            else:
                cantidad_colores -= 1  # Reducir la cantidad de colores si no es válido

            if cantidad_colores == len(colores_validos):
                print("PALETA GENERADA:")
                print("Color Principal: " + str(color_hsl_principal))
                for i, color in enumerate(colores_validos):
                    print(f"Color {i+1} Generado: {color}")

        # Convertir colores válidos a RGB
        paleta_rgb = [self._hsl_to_rgb(*color_hsl) for color_hsl in colores_validos]

        return {
            "color_principal": self._hsl_to_rgb(*color_hsl_principal),
            "colores_generados": paleta_rgb,
            "cantidad_colores": len(colores_validos)
        }



# Ejemplo de uso
if __name__ == '__main__':
    generador = GeneradorVibrantPalette("paso2_probabilidades/probabilidadesColorPrincipal_Vibrante.csv", "paso2_probabilidades/probabilidadesColorDiferencial_Vibrante.csv")
    paleta = generador.generar_paleta()
    print(paleta)
    
