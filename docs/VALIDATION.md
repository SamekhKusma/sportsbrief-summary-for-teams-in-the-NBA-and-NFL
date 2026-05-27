# Validation

Backend validation completed in the build environment.

Command used:

```bash
cd backend
python -m pytest -q
```

Result:

```text
5 passed
```

Frontend dependencies were not committed. Run this locally instead:

```bash
cd frontend
npm install
npm run build
npm run dev
```
