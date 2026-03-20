# PROJECT SOL — Context Log

## [2026-03-20 00:00] — MVP polish for first tester release
- What changed:
  - Fixed version mismatch: pyproject.toml updated from 2.0.0 to 2.2.0
  - Fixed journal typo: "SOL want to know" → "SOL wants to know"
  - Cleaned error messages: removed raw Python exception text from Gemini, Ollama, and LLM brain error responses
  - Fixed misleading Gemini fallback message: now directs users to say "change model" instead of falsely claiming auto-fallback
  - Created .env.example template for testers
  - Added thinking indicator: shows "[ thinking... ]" while waiting for API responses (skipped for instant pattern brain)
  - Added help command: type "help", "?", or "commands" to see available features
  - Updated README.md with help command in voice commands table and .env.example in project structure
- Why: Preparing SOL for first external tester — polishing loose ends without changing the core app
- Impact on project goals: MVP is now ship-ready for external testing
- Files modified:
  - files/pyproject.toml
  - files/src/sol/features/journal.py
  - files/src/sol/brain/gemini_brain.py
  - files/src/sol/brain/ollama_brain.py
  - files/src/sol/brain/llm_brain.py
  - files/src/sol/app.py
  - files/README.md
  - files/.env.example (new)
