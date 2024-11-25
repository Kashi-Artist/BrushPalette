// Mostrar el selector de color cuando se hace clic en "Sí"
document.getElementById('chooseColor').addEventListener('click', function() {
    let colorPickerContainer = document.getElementById('colorPickerContainer');
    colorPickerContainer.style.display = 'block'; // Mostrar el selector de color
});

// Ocultar el selector de color cuando se hace clic en "No" y resetear el valor a #000000
document.getElementById('chooseColorNo').addEventListener('click', function() {
    let colorPickerContainer = document.getElementById('colorPickerContainer');
    colorPickerContainer.style.display = 'none'; // Ocultar el selector de color
    document.getElementById('colorPrincipal').value = '#000000'; // Restablecer el color
});

// Manejar el envío del formulario de generación de paleta
document.getElementById('paletteForm').addEventListener('submit', function(event) {
    event.preventDefault();
    let colorPickerContainer = document.getElementById('colorPickerContainer');
    let colorPrincipal = document.getElementById('colorPrincipal').value;
    let estilo = document.getElementById('estilo').value;
    let tipoPaleta = document.getElementById('tipoPaleta').value;
    
    // Asigna el valor de color principal solo si se seleccionó el botón de "Sí"
    let colorPrincipalSeleccionado = (colorPickerContainer.style.display === 'block') ? colorPrincipal : null;

    let data = {
        color_principal: colorPrincipalSeleccionado ? hexToRgb(colorPrincipalSeleccionado) : null, // Convertir HEX a RGB si fue seleccionado
        estilo: estilo,
        tipo_paleta: tipoPaleta
    };
    console.log(data);

    fetch('generate_palette', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        displayResult(result);
    })
    .catch(error => {
        console.error('Hubo un problema con la solicitud Fetch:', error);
        document.getElementById('result').innerHTML = '<p>Error al generar la paleta. Por favor, intenta de nuevo.</p>';
    });
});

// Función para convertir HEX a RGB
function hexToRgb(hex) {
    let bigint = parseInt(hex.slice(1), 16);
    let r = (bigint >> 16) & 255;
    let g = (bigint >> 8) & 255;
    let b = bigint & 255;
    return [r, g, b];
}

// Mostrar el resultado de la paleta generada
function displayResult(result) {
    let resultDiv = document.getElementById('result');
    resultDiv.innerHTML = '';

    // Contenedor flex para colocar el color principal y los colores generados en una fila
    let rowContent = '<div class="row-colors">';

    // Color principal
    if (result.color_principal) {
        rowContent += `
            <div class="color-box-container">
                <h3 class="center-title">Color Principal:</h3>
                <div class="main-color-box" style="background-color: rgb(${result.color_principal.join(', ')});" ></div>
            </div>
        `;
    }

    // Colores generados
    let colorGrid = '<div class="color-box-container"><h3 class="center-title">Colores Generados:</h3><div class="color-grid">';
    result.colores_generados.forEach((color) => {
        const rgbString = `rgb(${color.join(', ')})`;
        colorGrid += `
            <div class="color-box" style="background-color: ${rgbString}">
                <button class="copy-btn" onclick="copyColor('${rgbString}')">Copiar</button>
            </div>
        `;
    });
    colorGrid += '</div></div>';
    
    rowContent += colorGrid;
    rowContent += '</div>'; // Cierra el contenedor de la fila

    resultDiv.innerHTML += rowContent;

    // Agrega la tabla de guía de colores
    let table = `
        <h3 class="center-title">Guía de Colores</h3>
        <table class="color-table">
            <tr>
                <th>Color Principal</th>
                <td>${result.color_principal ? `rgb(${result.color_principal.join(', ')})` : 'No seleccionado'}</td>
            </tr>
    `;
    result.colores_generados.forEach((color, index) => {
        table += `
            <tr>
                <th>Color ${index + 1} Generado</th>
                <td>rgb(${color.join(', ')})</td>
            </tr>
        `;
    });

    table += `</table>`;
    resultDiv.innerHTML += table;
}


// Función para copiar el valor RGB al portapapeles
function copyColor(color) {
    let tempInput = document.createElement('input');
    document.body.appendChild(tempInput);
    tempInput.value = color;
    tempInput.select();
    document.execCommand('copy');
    document.body.removeChild(tempInput);
    alert(`Color ${color} copiado al portapapeles!`);
}

// Manejar el envío del formulario para aplicar la paleta a la imagen
document.getElementById('imageForm').addEventListener('submit', function(event) {
    event.preventDefault();
    let formData = new FormData();
    let imageFile = document.getElementById('imageInput').files[0];
    formData.append('image', imageFile);

    fetch('apply_palette', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(result => {
        if (result.processed_image_url) {
            document.getElementById('processedImage').src = result.processed_image_url;
            document.getElementById('processedImageContainer').style.display = 'block';
        } else if (result.error) {
            alert(result.error);
        }
    })
    .catch(error => {
        console.error('Error al aplicar la paleta a la imagen:', error);
    });
});
