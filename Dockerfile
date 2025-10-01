# 1-qism: Quruvchi (Builder)
FROM python:3.10 AS builder
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# WeasyPrint uchun kerakli tizim paketlari
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libharfbuzz0b \
    libgobject-2.0-0 \
    fontconfig \
    fonts-liberation \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

RUN pip install pipenv

# --- BIZNING YECHIMIMIZ ---
# "exceptiongroup" paketini qo'lda, majburan o'rnatamiz
RUN pip install exceptiongroup
# -------------------------

WORKDIR /app
COPY Pipfile Pipfile.lock /app/
RUN pipenv install --system --deploy --ignore-pipfile


# 2-qism: Yakuniy Image
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Kerakli tizim paketlari va kutubxonalarni builder'dan ko'chiramiz
COPY --from=builder /usr/lib/ /usr/lib/
COPY --from=builder /lib/x86_64-linux-gnu /lib/x86_64-linux-gnu

# O'rnatilgan Python paketlarini va komandalarni ko'chiramiz
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Fontconfig xatoligini oldini olish uchun
COPY --from=builder /etc/fonts /etc/fonts

WORKDIR /app
COPY . /app/

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]