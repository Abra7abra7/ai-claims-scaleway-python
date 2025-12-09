# 🪝 Git Hooks - Automatická generácia typov

## Čo to robí?

Pri každom **`git commit`** sa automaticky:
1. ✅ Skontroluje či backend beží
2. 🔄 Vygenerujú TypeScript typy z OpenAPI
3. 📝 Pridajú sa do commitu (ak sa zmenili)

---

## 🚀 Ako to používať?

### Normálny workflow:

```bash
# 1. Spusti backend (ak ešte nebeží)
docker compose up -d backend

# 2. Urob zmeny v kóde
# ... edituj súbory ...

# 3. Commitni (hook sa spustí automaticky)
git add .
git commit -m "Add new feature"

# ✅ Typy sa vygenerujú automaticky!
```

### Výstup pri commite:

```
🔄 Pre-commit: Checking for TypeScript types updates...
✅ Backend is running
🔄 Generating TypeScript types...
✨ openapi-typescript 7.10.1
🚀 http://localhost:8000/api/v1/openapi.json → src/lib/api-types.ts
📝 Types updated - staging changes...
✅ TypeScript types generated and staged
```

---

## 📋 Scenáre

### Scenár 1: Backend beží ✅
Hook vygeneruje typy a pridá ich do commitu.

### Scenár 2: Backend nebeží ⚠️
```
⚠️  Backend is not running on localhost:8000
💡 Tip: Start backend with: docker compose up -d backend
⏭️  Skipping type generation (using existing types)
```
Commit pokračuje s existujúcimi typmi.

### Scenár 3: Typy sa nezmenili ✅
```
✅ Types are up to date
```
Nič sa nepridá do commitu.

---

## 🔧 Riešenie problémov

### Hook sa nespúšťa?

```bash
# Reinstaluj hooks
npm run prepare
```

### Chceš commitnúť bez hooku?

```bash
git commit -m "Message" --no-verify
```

### Skontroluj či hook existuje:

```bash
cat .husky/pre-commit
```

---

## 📁 Súbory

- `.husky/pre-commit` - Git hook
- `scripts/pre-commit-types.js` - Script pre generáciu
- `package.json` - Husky konfigurácia

---

## 💡 Tip pre tím

Každý vývojár si musí po klonovaní repo spustiť:

```bash
npm install
```

To automaticky nainštaluje Husky a nakonfiguruje hooks.

