# PR1: Duplicity Check, Best Practices, 360 Audit - Plan

## Step 1: Plan audit steps
- Pylint duplicity check
- Add async/logging/rate limiting in main.py
- JWT base in security.py
- Bandit scan/fix

## Step 2: Run pylint
- Check for code duplicity
- Fix any issues found

## Step 3: Update main.py with rate limit
- Add rate limiting middleware
- Enhance async handling

## Step 4: Add JWT stub in security.py
- Basic JWT functionality
- Token generation/validation

## Step 5: Bandit scan/fix
- Security vulnerability check
- Fix any security issues

## Anti-stuck rules:
- Work on one file at a time
- If any step takes >30s, pause and summarize
- Keep changes incremental
- Run tests after each major change
