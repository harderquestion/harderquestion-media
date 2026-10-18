# Harder Questions pipeline

`python3 render.py weekNN.json ../2026/wNN` renders a week of posts from a spec (see week43.json for the format):
- `reel`: question + followup -> 9 s MP4 (1080x1920) + cover JPG
- `carousel`: topic + three levels -> 4 PNG slides (1080x1350)
- `reading`: question + three fast answers -> 5 PNG slides

Requires Playwright (Chromium) and ffmpeg. Fonts: Lora, Inter.
Published media URL pattern: https://raw.githubusercontent.com/harderquestion/harderquestion-media/main/2026/wNN/<file>
