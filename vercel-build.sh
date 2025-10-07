#!/bin/bash

# Menginstal dependensi terlebih dahulu
pip install -r requirements.txt

# Menjalankan migrasi database menggunakan modul python
python -m flask db upgrade