FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy language models for Presidio
# Multilingual model for SK and general use (smaller, ~50MB)
RUN python -m spacy download xx_ent_wiki_sm
# German model for DE
RUN python -m spacy download de_core_news_sm
# Italian model for IT  
RUN python -m spacy download it_core_news_sm
# English model (small version for less RAM)
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY app.py .

# Expose port
EXPOSE 8001

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]

