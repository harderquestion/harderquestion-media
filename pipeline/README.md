# Harder Questions pipeline

`python3 render.py weekNN.json ../2026/wNN` renders a week of posts from a spec (see week43.json for the format):
- `reel`: question + followup -> 9 s MP4 (1080x1920) + cover JPG
- `carousel`: topic + three levels -> 4 PNG slides (1080x1350)
- `reading`: question + three fast answers -> 5 PNG slides

Requires Playwright (Chromium) and ffmpeg. Fonts: Lora, Inter.
Published media URL pattern: https://raw.githubusercontent.com/harderquestion/harderquestion-media/main/2026/wNN/<file>

## Brand frame (Oct 18)
Every Reel opens with the small copper line STOP HERE FOR A MINUTE and closes with "Scroll when you have an answer."
Carousels and reading posts carry the line on slide 1; the final slide reads "Seven more to stop for."
Captions: question (+ follow-up for Reels); 2-3 sentences of context in the note voice (never advice);
"Scroll when you have an answer."; "7 free questions in the bio." Hashtags in the first comment only.
Post ids carry a letter suffix when a week is re-rendered (d01b) so schedulers never see a cached old file.
