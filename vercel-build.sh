#!/bin/bash

# Menggunakan python3.9 (versi stabil di Vercel) untuk menginstal dependensi
python3.9 -m pip install -r requirements.txt

# Menggunakan python3.9 untuk menjalankan migrasi database
python3.9 -m flask db upgrade