# 1-qadam: Bazaviy image tanlaymiz.
FROM python:3.10-slim

# Muhit o'zgaruvchilarini sozlash
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 2-qadam: Tizim paketlarini o'rnatish. (Bu joyi to'g'ri ishlayapti)
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-xlib-2.0-0 \
    shared-mime-info \
    fonts-liberation \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# 3-qadam: Ishchi papkani yaratish
WORKDIR /app

# 4-qadam: Python bog'liqliklarini o'rnatish
RUN pip install pipenv

# --- MUAMMONING YECHIMI ---
# "exceptiongroup" paketini to'g'ridan-to'g'ri, majburan o'rnatamiz
RUN pip install exceptiongroup
# -------------------------

COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy --ignore-pipfile

# 5-qadam: Loyiha kodini to'liq ko'chirish
COPY . .

# 6-qadam: Static fayllarni yig'ish (Production uchun muhim)
RUN python manage.py collectstatic --no-input --clear

# 7-qadam: Portni ochish va serverni ishga tushirish
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]