# FK94 Platform - Deploy Instructions

## Backend (FastAPI) en Render

1. Ir a https://render.com y hacer login con GitHub
2. Click "New" → "Web Service"
3. Conectar el repo `FK94SECURITY/fk94platform`
4. Configurar:
   - Name: `fk94-api`
   - Root Directory: `backend`
   - Runtime: `Docker`
   - Instance Type: `Free`
5. Agregar variables de entorno (copiar de backend/.env):
   ```
   DEEPSEEK_API_KEY=<tu API key de DeepSeek>
   HIBP_API_KEY=<tu API key de HIBP>
   STRIPE_SECRET_KEY=<tu Stripe secret key>
   STRIPE_PUBLISHABLE_KEY=<tu Stripe publishable key>
   ```
6. Click "Create Web Service"
7. Copiar la URL del servicio (ej: `https://fk94-api.onrender.com`)

## Frontend (Next.js) en Vercel

1. Ir a https://vercel.com y hacer login con GitHub
2. Click "Add New" → "Project"
3. Importar el repo `FK94SECURITY/fk94platform`
4. Configurar:
   - Framework Preset: `Next.js`
   - Root Directory: `frontend`
5. Agregar variables de entorno:
   ```
   NEXT_PUBLIC_API_URL=https://fk94-api.onrender.com  (la URL del paso anterior)
   NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=<tu Stripe publishable key>
   ```
6. Click "Deploy"

## Resultado Final

- Frontend: https://fk94platform.vercel.app (o dominio custom)
- Backend: https://fk94-api.onrender.com
- Docs API: https://fk94-api.onrender.com/docs

## Dominio Custom (opcional)

Para usar `fk94security.com`:
1. En Vercel, ir a Settings → Domains
2. Agregar `fk94security.com` y `www.fk94security.com`
3. En tu DNS (Cloudflare, GoDaddy, etc.), agregar los registros que Vercel te indica
