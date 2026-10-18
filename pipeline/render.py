"""Render a week of Harder Questions posts from a JSON spec.

Usage: python3 render.py week.json OUT_DIR
Produces OUT_DIR/<post id>.mp4 for reels, OUT_DIR/<post id>_1..N.png for carousels/readings,
and OUT_DIR/manifest.json listing files per post.
"""
import json, os, sys, subprocess, shutil, time, html
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(HERE, "templates")
FPS, SECS = 30, 10

def fill(tpl, mapping):
    out = tpl
    for k, v in mapping.items():
        out = out.replace("{{" + k + "}}", v)
    return out

def qsize(text):
    n = len(text)
    return "84" if n <= 60 else "74" if n <= 85 else "66"

def hsize(text):
    n = len(text)
    return "92" if n <= 45 else "80" if n <= 70 else "68"

def render_reel(pg, post, out_dir, work):
    tpl = open(os.path.join(TPL, "reel.html"), encoding="utf-8").read()
    page = fill(tpl, {
        "QUESTION_JSON": json.dumps(post["question"]),
        "FOLLOWUP": html.escape(post["followup"]),
        "DAY": str(post["day"]),
        "SEED": str(post["day"]),
        "QSIZE": qsize(post["question"]),
    })
    p = os.path.join(work, post["id"] + ".html")
    open(p, "w", encoding="utf-8").write(page)
    frames = os.path.join(work, post["id"] + "_frames"); os.makedirs(frames, exist_ok=True)
    pg.set_viewport_size({"width": 1080, "height": 1920})
    pg.goto("file://" + p); pg.wait_for_timeout(250)
    for i in range(FPS * SECS):
        pg.evaluate(f"render({i/FPS})")
        pg.screenshot(path=os.path.join(frames, f"f_{i:04d}.jpg"), type="jpeg", quality=92)
    mp4 = os.path.join(out_dir, post["id"] + ".mp4")
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-framerate", str(FPS), "-i", os.path.join(frames, "f_%04d.jpg"),
        "-f", "lavfi", "-i", f"anoisesrc=color=brown:amplitude=0.02:duration={SECS}:sample_rate=44100:seed={post['day']}",
        "-filter_complex", f"[1:a]lowpass=f=180,afade=t=in:d=1.5,afade=t=out:st={SECS-1.5}:d=1.5[a]",
        "-map", "0:v", "-map", "[a]",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", "-preset", "medium",
        "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", "-shortest", mp4], check=True)
    shutil.rmtree(frames)
    # cover frame at 4.0s for thumbnail
    cover = os.path.join(out_dir, post["id"] + "_cover.jpg")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "4.0", "-i", mp4, "-frames:v", "1", "-q:v", "2", cover], check=True)
    return [mp4, cover]

def render_slides(pg, post, out_dir, work, slides):
    tpl = open(os.path.join(TPL, "slide.html"), encoding="utf-8").read()
    files = []
    pg.set_viewport_size({"width": 1080, "height": 1350})
    for i, s in enumerate(slides, 1):
        page = fill(tpl, {
            "THEME": s.get("theme", ""),
            "NUM": s.get("num", f"{i} / {len(slides)}"),
            "PAUSE": '<div class="pause">STOP HERE FOR A MINUTE</div>' if s.get("pause") else "",
            "KICKER": html.escape(s.get("kicker", "")),
            "HEADLINE": html.escape(s["headline"]),
            "HSIZE": s.get("hsize") or hsize(s["headline"]),
            "SUB": s.get("sub", ""),
            "SUBTOP": s.get("subtop", "900"),
            "ARROW": '<div class="arrow">&rarr;</div>' if i < len(slides) else "",
            "FOOTR": "Swipe" if i < len(slides) else "@harderquestion",
        })
        p = os.path.join(work, f"{post['id']}_{i}.html")
        open(p, "w", encoding="utf-8").write(page)
        png = os.path.join(out_dir, f"{post['id']}_{i}.png")
        pg.goto("file://" + p); pg.wait_for_timeout(200)
        pg.screenshot(path=png)
        files.append(png)
    return files

def carousel_slides(post):
    s = [{"kicker": f"{post['topic']} · {lvl}", "headline": q, "num": f"{i} / 4", "pause": i == 1} for i, (lvl, q) in enumerate(post["levels"], 1)]
    s.append({"theme": "dark", "kicker": "SEVEN FREE QUESTIONS", "headline": "Seven more to stop for.", "num": "4 / 4",
              "sub": "A free starter set: one question per page, one follow-up that makes it harder, room to write.<br><br><b>Link in bio.</b>", "subtop": "860"})
    return s

def reading_slides(post):
    s = [{"kicker": "READING YOUR ANSWER", "headline": post["question"], "num": "1 / 5", "pause": True,
          "sub": "Three answers that come fast, and what each one tends to protect.", "subtop": "960"}]
    for i, (ans, note) in enumerate(post["answers"], 2):
        s.append({"kicker": f"A FAST ANSWER · {i-1}", "headline": ans, "num": f"{i} / 5", "sub": note, "subtop": "860"})
    s.append({"theme": "dark", "kicker": "SEVEN FREE QUESTIONS", "headline": "Seven more to stop for.", "num": "5 / 5",
              "sub": "A free starter set: one question per page, one follow-up that makes it harder, room to write.<br><br><b>Link in bio.</b>", "subtop": "860"})
    return s

def main():
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    out_dir = sys.argv[2]; os.makedirs(out_dir, exist_ok=True)
    work = os.path.join(HERE, "work"); os.makedirs(work, exist_ok=True)
    manifest = {}
    t0 = time.time()
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        for post in spec["posts"]:
            if post["kind"] == "reel":
                files = render_reel(pg, post, out_dir, work)
            elif post["kind"] == "carousel":
                files = render_slides(pg, post, out_dir, work, carousel_slides(post))
            elif post["kind"] == "reading":
                files = render_slides(pg, post, out_dir, work, reading_slides(post))
            manifest[post["id"]] = [os.path.basename(f) for f in files]
            print(post["id"], "done", round(time.time() - t0), "s", flush=True)
        b.close()
    json.dump(manifest, open(os.path.join(out_dir, "manifest.json"), "w"), indent=1)
    print("all done", round(time.time() - t0), "s")

if __name__ == "__main__":
    main()
