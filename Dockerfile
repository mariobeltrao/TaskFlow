FROM node:22-alpine AS frontend-build
WORKDIR /build/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
ARG VITE_ENABLE_GOOGLE_INTEGRATION=false
ENV VITE_ENABLE_GOOGLE_INTEGRATION=$VITE_ENABLE_GOOGLE_INTEGRATION
RUN npm run build

FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8000
WORKDIR /app
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt \
    && addgroup --system taskflow \
    && adduser --system --ingroup taskflow --home /app taskflow
COPY backend/app /app/backend/app
COPY backend/alembic /app/backend/alembic
COPY backend/alembic.ini /app/backend/alembic.ini
COPY --from=frontend-build /build/frontend/dist /app/frontend/dist
COPY --chmod=755 docker/entrypoint.sh /app/entrypoint.sh
RUN chown -R taskflow:taskflow /app
USER taskflow
WORKDIR /app/backend
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import os,urllib.request; urllib.request.urlopen('http://127.0.0.1:'+os.environ.get('PORT','8000')+'/api/health',timeout=3)"
ENTRYPOINT ["/app/entrypoint.sh"]
