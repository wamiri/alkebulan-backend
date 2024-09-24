FROM python@sha256:80619a5316afae7045a3c13371b0ee670f39bac46ea1ed35081d2bf91d6c3dbd

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY Pipfile Pipfile.lock ./
RUN python -m pip install --upgrade pip
RUN pip install pipenv && pipenv install --system --deploy

RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser

COPY . .

CMD ["fastapi", "run", "src/main.py", "--port", "8000"]