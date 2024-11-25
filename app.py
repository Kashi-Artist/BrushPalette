from flask import Flask, request, jsonify, render_template, url_for
from PIL import Image
from io import BytesIO
import os
from algoritmoGenerativo_Minimalista import GeneradorMinimalistPalette
from algoritmoGenerativo_Abstracto import GeneradorAbstractPalette
from algoritmoGenerativo_Vibrante import GeneradorVibrantPalette

app = Flask(__name__)

# Ruta principal para renderizar el HTML
@app.route('/')
def home():
    return render_template('index.html')


# Ruta para generar la paleta de colores
@app.route('/generate_palette', methods=['POST'])
def generate_palette():
    data = request.get_json()
    color_principal = data['color_principal']
    estilo = data['estilo']
    tipo_paleta = data['tipo_paleta']

    if estilo == 'Minimalista':
        generador = GeneradorMinimalistPalette(
            "paso2_probabilidades/probabilidadesColorPrincipal_Minimalista.csv",
            "paso2_probabilidades/probabilidadesColorDiferencial_Minimalista.csv",
            color_principal,
            tipo_paleta
        )
    elif estilo == 'Abstracto':
        generador = GeneradorAbstractPalette(
            "paso2_probabilidades/probabilidadesColorPrincipal_Abstracto.csv",
            "paso2_probabilidades/probabilidadesColorDiferencial_Abstracto.csv",
            color_principal,
            tipo_paleta
        )
    elif estilo == 'Vibrante':
        generador = GeneradorVibrantPalette(
            "paso2_probabilidades/probabilidadesColorPrincipal_Vibrante.csv",
            "paso2_probabilidades/probabilidadesColorDiferencial_Vibrante.csv",
            color_principal,
            tipo_paleta
        )

    colores_generados = generador.generar_paleta()

    # Generar paleta hasta que haya al menos tres colores
    while len(colores_generados['colores_generados']) < 3:
        colores_generados = generador.generar_paleta()

    app.config['colores_generados'] = colores_generados['colores_generados']
    print("Colores generados:", colores_generados['colores_generados'])  # Debugging

    return jsonify({
        'color_principal': colores_generados['color_principal'],
        'colores_generados': colores_generados['colores_generados']
    })


# Ruta para aplicar la paleta generada a la imagen
@app.route('/apply_palette', methods=['POST'])
def apply_palette():
    if 'colores_generados' not in app.config:
        return jsonify({'error': 'Primero genera una paleta antes de aplicar colores a la imagen.'}), 400

    image_file = request.files['image']
    img = Image.open(image_file).convert('RGB')  # Asegúrate de que la imagen esté en formato RGB

    # Convertir colores a tuplas RGB si están en formato hexadecimal
    colores = app.config.get('colores_generados', [])
    colores = [hex_to_rgb(color) if isinstance(color, str) else color for color in colores]

    output_img = img.copy()
    width, height = output_img.size

    # Mapea los colores generados a la imagen
    for x in range(width):
        for y in range(height):
            pixel = img.getpixel((x, y))
            closest_color = find_closest_color(pixel, colores)
            output_img.putpixel((x, y), closest_color)

    # Asegúrate de que el directorio exista
    output_dir = os.path.join('static', 'processed_images')
    os.makedirs(output_dir, exist_ok=True)

    # Guardar la imagen en el directorio estático
    output_path = os.path.join(output_dir, 'imagen_modificada.png')
    output_img.save(output_path)

    return jsonify({
        'processed_image_url': url_for('static', filename='processed_images/imagen_modificada.png')
    })


# Función para encontrar el color más cercano
def find_closest_color(pixel, colores):
    r, g, b = pixel
    closest_color = min(colores, key=lambda color: (r - color[0]) ** 2 + (g - color[1]) ** 2 + (b - color[2]) ** 2)
    return tuple(closest_color)


# Función para convertir colores hexadecimales a RGB
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5004))
    app.run(debug=True, host='0.0.0.0', port=port)
