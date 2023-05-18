# Menggunakan base image python:3.9-slim-buster
FROM python:3.9-slim-buster

# Menentukan working directory
WORKDIR /app

# Menyalin file requirements.txt ke dalam image
COPY requirements.txt .

# Menginstal dependensi yang diperlukan
RUN pip install --no-cache-dir -r requirements.txt

# Menyalin seluruh konten aplikasi ke dalam image
COPY . .

# Menjalankan perintah untuk menjalankan aplikasi
CMD [ "python", "app.py" ]
