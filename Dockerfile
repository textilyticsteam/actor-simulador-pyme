FROM apify/actor-python:3.11

# Copia e instala dependencias primero para aprovechar la caché
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del proyecto (incluyendo modelos/ y src/)
COPY . ./

# Ejecuta el módulo principal
CMD ["python3", "-m", "src"]