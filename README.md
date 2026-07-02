# JD Ingestion System

Production-style FastAPI backend for ingesting messy job description documents and converting them into validated, chunked, embedded records stored in FAISS.

## Architecture

Pipeline flow:

1. Detect input type (`pdf`, `docx`, `image`, `url`, `raw_text`)
2. Extract text (PyMuPDF, python-docx, pytesseract, trafilatura)
3. Clean noisy text
4. Segment into JD blocks (rule-based + optional Gemini)
5. Validate JD blocks
6. Store raw + processed content + metadata
7. Chunk text (500-word chunks)
8. Generate embeddings (`all-MiniLM-L6-v2`)
9. Store vectors + metadata in FAISS

## Project Structure

```text
jd_ingestion_system/
  app/
    main.py
    api/
      routes_ingest.py
      routes_admin.py
    core/
      config.py
      logging.py
    pipeline/
      ingestion_pipeline.py
      input_detector.py
      extractors/
        pdf_extractor.py
        docx_extractor.py
        image_extractor.py
        url_extractor.py
    processing/
      cleaner.py
      segmenter.py
      validator.py
      chunker.py
    llm/
      gemini_segmenter.py
    storage/
      vector_store.py
      metadata_store.py
      file_store.py
    models/
      schemas.py
    utils/
      hashing.py
      text_utils.py
  data/
    raw/
    processed/
  requirements.txt
```

## Run Locally

```bash
cd jd_ingestion_system
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open Swagger UI at `http://127.0.0.1:8000/docs`.

## API Usage

### Ingest file

```bash
curl -X POST http://127.0.0.1:8000/ingest \
  -F "file=@sample_jobs.pdf"
```

### Ingest URL

```bash
curl -X POST http://127.0.0.1:8000/ingest \
  -F "url=https://example.com/jobs-page"
```

### Get processed jobs

```bash
curl http://127.0.0.1:8000/jobs
curl http://127.0.0.1:8000/jobs/{job_id}
curl http://127.0.0.1:8000/stats
```

## Notes

- Max upload size: 10 MB.
- Use `async_mode=true` on `/ingest` to run heavy ingestion via FastAPI background tasks.
- Set `.env` with `USE_LLM_SEGMENTATION=true` and `GEMINI_API_KEY=...` to enable optional LLM-assisted splitting.
