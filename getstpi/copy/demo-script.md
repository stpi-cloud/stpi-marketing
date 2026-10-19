# STPi — demo scripts

Before the demo, have ready (5 min of prep):
- [ ] your Discord open on #stpi with 2–3 real cards visible (or run one manually:
      Actions → hunt → Run workflow; ~5 min)
- [ ] one card you can approve live (or a pre-recorded phone clip of the tap)
- [ ] the sample CV + cover letter open (samples/ in this repo)
- [ ] the pricing line you've decided (see pricing section on the hub)

---

## The 5-minute demo

**0:00 — the pain (30 s)**
"Show me your Tuesday. Six boards, forty tabs, the same letter rewritten per candidate.
That's the job nobody bills for. Watch what mine looks like instead."

**0:30 — the card (90 s)** *open Discord*
"This is it. One channel, one card per opportunity."
Read it slowly, point at each line:
- "The board and the role — this one came off CareerJunction at 90% match."
- "The match reason is one human-readable sentence, not a score dump."
- "Both PDFs are attached. Open the letter — see the second paragraph? It names the
  company and matches two real requirements. It's built from the candidate's actual
  bullets, and the system is forbidden from inventing anything."
- "And the two buttons. Approve, reject. That's my whole interface."

**2:00 — the tap (60 s)**
"Watch a real send." Tap ✅ → show the confirmation → "Sent from my mailbox, signed
as the candidate. When the employer answers, it reaches the candidate and me, and STPi
pings me if it's an interview. The employer gets a normal human email.
Now reject one." Tap ❌ → "Deleted. The PDFs are gone the moment you decide. Untouched
cards self-destruct after 72 hours."

**3:00 — the three fears (60 s)** — answer before they ask:
1. "Does it apply by itself? No. Every send is your tap. It's a pipeline for your
   judgement, not a replacement for it."
2. "Will it invent things? It can't — the writer only reorders and rephrases what's on
   the profile. Here's the sample CV next to the letter; check me."
3. "Spam risk? Sends go through my mailbox, capped at 20 per candidate and 150 a day, and
   every one is human-approved. That's cleaner than most manual spraying."

**4:00 — the money (60 s)**
"No server. It runs on two GitHub Actions workflows on a private repo — $0, no card.
You're not buying infrastructure; you're buying your Tuesdays back."
State price. Close with the demo stack:
"The demo is free forever — one candidate, five sends a month, no card.
Solo is $306 a month (about R4,999) for three candidates when your bench asks for it. Set the demo
up now while we're on the phone; a first card appears only when a suitable new job is found."
Landing page (lead capture + download): https://getstpi.pages.dev/demo

---

## The 15-minute deep dive (studio / agency buyers)

5-min demo above, then:
- **6 min — coverage matrix**: open the board list (ZA: Adzuna · Google for Jobs · PNet ·
  CareerJunction · JobMail · Bizcommunity · LinkedIn · remote. ZW: VacancyMail · iHarareJobs · JobsZimbabwe.
  ZM: GoZambiaJobs). "22 boards supported, 17 on by default; some boards block datacentre IPs, the pipeline
  degrades board-by-board without ever stopping — one dead scraper never kills a run."
- **8 min — economics**: one LLM call per shortlisted job does score + letter + CV; rules
  and pre-scoring reject ~85% of ads for free before any AI spend. "Your API bill is in
  cents because triage is free and judgement is scarce."
- **10 min — data posture**: active generated-content expiry; store keeps `{job_url, status, timestamp}`;
  candidate YAML is the right to erasure (delete file = gone); no LinkedIn login.
- **12 min — billing rails**: Whop subscription, Lightning via coinos for ZW/ZM, Mukuru
  handled as a manual grant. "Your customers pay how they already pay."
- **14 min — modes**: hosted (you run it for your clients) vs self-hosted (an agency runs
  their own box, licence-checked daily, read-only on expiry, never bricked).

---

## 45-second video script (screen record + captions)

```
SHOT 1 (0:00-0:08)  Screen: 12 browser tabs open, clock ticking.
CAPTION: "Tuesday, 6 boards, 40 tabs."

SHOT 2 (0:08-0:18)  Discord: a card appears.
CAPTION: "STPi hunted so I didn't. One card. Match 90%."

SHOT 3 (0:18-0:28)  Open the letter PDF, scroll.
CAPTION: "Letter + CV drafted from the candidate's real profile. Nothing invented."

SHOT 4 (0:28-0:36)  Phone: tap ✅. Sent confirmation.
CAPTION: "My tap. Sent, signed as them — or packed and ready for the portal."

SHOT 5 (0:36-0:45)  Logo on lilac.
VOICE/CAPTION: "STPi. Jobs found. Applications drafted. You tap approve. It sends."
```

## Post-demo email (send within an hour)

```
Great speaking, {{first_name}}.

What you saw, in one line: STPi hunts country-specific sources (keys and availability vary), drafts the letter + CV,
and waits for your tap.

Attached/below: the sample CV + letter, the guard-rails list, pricing.

The pilot stands: one candidate, one week, free. I'll set your webhook on
the call — onboarding is ~10 minutes.

— {{your_name}}
```
