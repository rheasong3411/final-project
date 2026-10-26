# Demo video draft (2026-10-26)

`demo_video_draft.webm`: 2 min 27 s, 1280×720, silent with on-screen captions. Recorded with Playwright on the final build
(test server port 8002, fresh calls). It's a real example from start to finish, with synthetic inputs and test ZIP 06511:
- Home;
- Explore with a cats filter and distance sort;
- a detail page with conflicting age sources and "Check my fit";
- Compare;
- a real Find my fit conversation (gpt-6-luna via Portkey, run `017a85eb1ddd`) with cards, "Your answers" and "Run
  details";
- a real safety test (run `1b0069441159`), where the "approval" is refused and the 21+ rule holds.

The assignment asks for a narrated recording, so Rhea may record her voice over it or upload it as is. It's optional,
and a backup for "It works" and "Look + feel" only.

- `traces/`: the four real runs from both takes (`7e0fa385aac6` and `65abaa1b620e` are from take 1).
- Take 1 (2 min 54 s) was superseded: one caption outlasted its page, and the comparison bar covered the chat. Its video
  is kept on the Mac in `local_data/demo_video_take1/`, not in the repository.
- Script: `demo_video_script.py`.
