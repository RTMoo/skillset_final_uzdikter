FROM python:3.12-alpine


# Установка рабочей директории
WORKDIR /backend

# Создание виртуального окружения
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Копируем зависимости и устанавливаем их
COPY backend/requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копируем весь проект
COPY backend /backend
