# API de predicción de abandono bancario

Aplicación FastAPI con preprocesamiento determinista, modelo KNN y frontend responsive.

## Ejecución local

```bash
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

- Interfaz web: <http://127.0.0.1:8000/>
- Swagger UI: <http://127.0.0.1:8000/docs>

## Uso

1. Abre `/`.
2. Introduce los datos del cliente o conserva los valores de ejemplo.
3. Pulsa **Calcular riesgo**.
4. Consulta la clase, la probabilidad, el nivel de riesgo y la acción recomendada.

También puedes probar `POST /predict` desde `/docs` con el JSON de ejemplo mostrado automáticamente por Swagger.

## Despliegue en Render

1. Crea un repositorio con el contenido de esta carpeta.
2. En Render, selecciona **New > Blueprint** y usa `render.yaml`.
3. Espera a que termine el build con Python 3.11 y Scikit-learn 1.6.1.
4. Registra la URL pública generada por Render en este documento.

### URL pública de producción

Pendiente de despliegue: `https://NOMBRE-DE-TU-SERVICIO.onrender.com`

### Verificación obligatoria

- Interfaz `/`: debe mostrar el formulario y ejecutar una inferencia real.
- Documentación `/docs`: debe permitir ejecutar `POST /predict`.
- Captura de pantalla: sustituye este párrafo por `![Inferencia en producción](captura-produccion.png)` cuando tengas la URL activa.

## Artefactos

Los archivos `artifacts/preprocesador_banca.joblib` y `artifacts/modelo_knn.joblib` deben conservarse en el repositorio y no deben modificarse.
