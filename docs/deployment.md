# Deployment Guide

The production topology should keep the clients public and the processing services private where possible:

```text
Web client / Mobile client -> Express API -> FastAPI ML service
                                      -> Supabase database and Storage
```

## Service Order

Deploy and verify services in this order:

1. Supabase schema and private `documents` Storage bucket.
2. FastAPI ML service.
3. Express backend.
4. React web build.
5. Expo mobile build.

For the selected hosting plan, use Vercel for `frontend/` and Render for the two services. The repository includes [render.yaml](../render.yaml) and [frontend/vercel.json](../frontend/vercel.json).

## FastAPI ML Service

Required production variables:

```env
HOST=0.0.0.0
PORT=8000
MYANMAR_NER_MODEL_PATH=/app/models/myanmar-ner-final
NER_MAX_LENGTH=512
MAX_CHUNK_CHARACTERS=12000
LLM_API_URL=https://api.openai.com/v1/chat/completions
LLM_API_KEY=<server-only-secret>
LLM_MODEL=<configured-model>
LLM_TIMEOUT_SECONDS=120
```

Start command:

```powershell
uvicorn app.main:app --host 0.0.0.0 --port $env:PORT
```

Health check:

```powershell
curl.exe https://<ml-service-host>/health
```

The NER model loads lazily on the first NER request. Keep enough memory available for the transformer model and expect the first NER request to be slower.

## Express Backend

Required production variables:

```env
PORT=3000
ML_SERVICE_URL=https://<private-ml-service-host>
MAX_FILE_SIZE_MB=25
CORS_ORIGIN=https://<web-host>,https://<mobile-web-host>
SUPABASE_URL=https://<project>.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<server-only-secret>
SUPABASE_STORAGE_BUCKET=documents
```

Start command:

```powershell
npm ci --omit=dev
npm start
```

Health check:

```powershell
curl.exe https://<api-host>/health
```

Only expose the Express API publicly. Keep the ML service restricted to backend traffic when the hosting platform supports private networking.

## React Web Client

Set `VITE_API_BASE_URL` to the public Express URL when the web host does not proxy `/api` and `/health`:

```env
VITE_API_BASE_URL=https://<api-host>
```

Build and publish the generated `frontend/dist` directory:

```powershell
npm ci
npm run build
```

On Vercel, import the repository, set the project root to `frontend`, and configure `VITE_API_BASE_URL` to the public Render API URL before building.

Never place Supabase service-role credentials or LLM API keys in Vite variables. Vite variables are included in the browser bundle.

## Expo Mobile Client

Set the public backend URL before starting or building the mobile client:

```env
EXPO_PUBLIC_API_BASE_URL=https://<api-host>
```

Use an HTTPS API URL for production builds. The backend must allow the mobile client to reach `/api/process`; native requests do not send a browser `Origin` header.

Expo iOS Simulator requires macOS and Xcode and cannot run on this Windows workstation. Use a physical iPhone with Expo Go from a macOS development machine, or verify Android locally with an emulator or physical Android device.

## Supabase

Apply [backend/supabase/schema.sql](../backend/supabase/schema.sql) to the production project and create a private Storage bucket named `documents`.

Verify after deployment:

- A processed PDF creates one `documents` row.
- Extracted entities create rows in `entities`.
- The generated summary creates one row in `summaries`.
- Uploaded files are stored only in the private `documents` bucket.

## Release Checklist

- Use HTTPS for the web client, API, and mobile API URL.
- Store secrets in the hosting provider's secret manager.
- Keep `SUPABASE_SERVICE_ROLE_KEY` and `LLM_API_KEY` server-only.
- Set `CORS_ORIGIN` to exact production origins, separated by commas.
- Confirm `MAX_FILE_SIZE_MB` matches available memory and request limits.
- Test `/health` for both services after deployment.
- Upload a representative Burmese PDF and verify extraction, NER, summary, and persistence.
- Review logs for failed ML calls, failed Supabase writes, and rejected uploads.
- Run the `document_results` view statement from [backend/supabase/schema.sql](../backend/supabase/schema.sql) in the Supabase SQL Editor.
- Ensure the ignored `ml-service/models/` directory is supplied to Render through a private model artifact or deployment storage; the Render service cannot load a model that is absent from the deployed source.
