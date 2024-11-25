import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
# Añadir la ruta del directorio padre para que se puedan importar los módulos
#sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# Importar cada procesamiento de color según su jerarquía visual
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)
from paso1_procesamientoImagenes.color_processingEspiral import (ColorExtractorEspiral,CalculodeResultadosEspiral,JerarquiaVisualEspiral)

from paso1_procesamientoImagenes.color_processingDiagonal import (ColorExtractorDiagonal,CalculodeResultadosDiagonal,JerarquiaVisualDiagonal)

from paso1_procesamientoImagenes.color_processingSimetria import (ColorExtractorSimetria,CalculodeResultadosSimetria,JerarquiaVisualSimetria)

from paso1_procesamientoImagenes.color_processingTercios import (ColorExtractorTercios,CalculodeResultadosTercios,JerarquiaVisualTercios)


def process_image(image_path):
    """Procesa una imagen utilizando 4 tipos de jerarquía visual y devuelve los colores en HSL."""
    print(f"Procesando {image_path}...")

    all_results = []

    # 1. Espiral Áurea (Extraer el color principal una sola vez)
    print(f"Extracción jerarquía visual: Espiral Áurea.")
    extractor_espiral = ColorExtractorEspiral(image_path)
    main_color_general = extractor_espiral.extract_main_color() # Extraer color principal aquí

    jerarquia_espiral = JerarquiaVisualEspiral(extractor_espiral.width, extractor_espiral.height)
    points_espiral = jerarquia_espiral.calculate_spiral_points()
    hierarchy_colors_espiral = extractor_espiral.extract_visual_hierarchy_colors(points_espiral)
    resultados_espiral = CalculodeResultadosEspiral(hierarchy_colors_espiral, main_color_general).calcular_promedios(image_path)
    resultados_espiral['Jerarquia'] = 'Espiral'
    all_results.append(resultados_espiral)

    # 2. Diagonal (Reutilizar el color principal)
    print(f"Extracción jerarquía visual: Diagonal.")
    extractor_diagonal = ColorExtractorDiagonal(image_path)
    jerarquia_diagonal = JerarquiaVisualDiagonal(extractor_diagonal.width, extractor_diagonal.height)
    points_diagonal = jerarquia_diagonal.calculate_diagonal_points()
    hierarchy_colors_diagonal = extractor_diagonal.extract_visual_hierarchy_colors(points_diagonal)
    resultados_diagonal = CalculodeResultadosDiagonal(hierarchy_colors_diagonal).calcular_promedios(image_path)
    resultados_diagonal['Jerarquia'] = 'Diagonal'
    all_results.append(resultados_diagonal)

    # 3. Simetría (Reutilizar el color principal)
    print(f"Extracción jerarquía visual: Simetria.")
    extractor_simetria = ColorExtractorSimetria(image_path)
    jerarquia_simetria = JerarquiaVisualSimetria(extractor_simetria.width, extractor_simetria.height)
    points_simetria = jerarquia_simetria.calculate_symmetric_points()
    hierarchy_colors_simetria = extractor_simetria.extract_visual_hierarchy_colors(points_simetria)
    resultados_simetria = CalculodeResultadosSimetria(hierarchy_colors_simetria).calcular_promedios(image_path)
    resultados_simetria['Jerarquia'] = 'Simetria'
    all_results.append(resultados_simetria)

    # 4. Tercios (Reutilizar el color principal)
    print(f"Extracción jerarquía visual: Tercios.")
    extractor_tercios = ColorExtractorTercios(image_path)
    jerarquia_tercios = JerarquiaVisualTercios(extractor_tercios.width, extractor_tercios.height)
    points_tercios = jerarquia_tercios.calculate_rule_of_thirds_points()
    hierarchy_colors_tercios = extractor_tercios.extract_visual_hierarchy_colors(points_tercios)
    resultados_tercios = CalculodeResultadosTercios(hierarchy_colors_tercios).calcular_promedios(image_path)
    resultados_tercios['Jerarquia'] = 'Tercios'
    all_results.append(resultados_tercios)

    return all_results


def process_images_parallel(image_folder, max_workers=4):
    """Procesa todas las imágenes de una carpeta en paralelo."""
    image_files = [os.path.join(image_folder, f) for f in os.listdir(
        image_folder) if f.endswith(('.jpg', '.jpeg', '.png'))]
    all_results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_image, img): img for img in image_files}
        for future in as_completed(futures):
            try:
                result = future.result()
                all_results.extend(result)  # Agregar los resultados de cada imagen
            except Exception as e:
                print(f"Error procesando {futures[future]}: {e}")

    return all_results

# código Original "AnalisisResultados_probabilitiesAbstract" o probabilitiesMinimalist
def save_to_csv(results, output_path="paso1_procesamientoImagenes/imagesVibrant/AnalisisResultados_probabilitiesVibrant.csv"):
    """Exporta los resultados a un archivo CSV."""
    df = pd.DataFrame(results)
    df.to_csv(output_path, index=False)
    print(f"Resultados exportados a {output_path}")


if __name__ == "__main__":
    # Procesar todas las imágenes en la carpeta especificada
    # código Original solo una carpeta a la vez 50 imagenes Tiempo Ejecución:(1074 seconds =18 minutos)
    # image_folder = "imagesAbstract"
    image_folder = "paso1_procesamientoImagenes/imagesVibrant"
    results = process_images_parallel(image_folder, max_workers=8)

    # Guardar resultados en CSV
    save_to_csv(results)
