# Use an official lightweight Python image
FROM python:3.9-slim


WORKDIR /app


COPY requirements.txt .


RUN pip install -r requirements.txt


COPY . .


ENV FLASK_ENV=production
ENV FLASK_DEBUG=0
ENV LMSTUDIO_BASE_URL="http://host.docker.internal:1234/v1"
ENV LMSTUDIO_API_KEY="lm-studio"


EXPOSE 8080


RUN crawl4ai-setup

# Crawl4ai-doctor returns 1 even on success for some reason. this ignores it. not ideal, but yeah.
RUN crawl4ai-doctor || true


CMD ["python", "server.py"]
