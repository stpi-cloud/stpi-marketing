# STPi — lifecycle email sequences

Customer = the coach (tenant owner). Tone: plain, specific, no exclamation inflation.

---

## Day 0 — welcome + setup (send the moment they sign up)

```
Subject: STPi is live for {{tenant}} — 3 clicks to first card

Hi {{name}},

Welcome. Your pipeline already has a home; it just needs three things from you:

1. DISCORD (2 min)
   In your server: #stpi → Edit Channel → Integrations → Webhooks → New Webhook.
   Paste the URL into your tenant.yaml under discord_webhook (I did this with you
   on the call — skip if done).

2. GMAIL APP PASSWORD (2 min)
   Switch on 2-step verification, then myaccount.google.com/apppasswords →
   create one → 16 characters. It lives encrypted in your tenant config; there is
   no Google Cloud project and no OAuth anywhere.

3. YOUR FIRST CANDIDATE (5 min)
   One YAML: name, country, location, keywords, exclusions. Copy the example —
   "accountant / bookkeeper / Johannesburg" is a proven starter.

That's it. Hunts run 06:00 / 10:00 / 14:00 / 18:00 (SAST), Mon–Sat.
Your first card should land within a few hours.

— The STPi desk
```

## Day 2 — expectation-setting

```
Subject: what a good first 48 hours looks like

Hi {{name}},

Two days in, here's what "normal" looks like:

- A handful of cards, not hundreds. STPi pre-scores every ad for free and only
  spends AI attention on the shortlist. Quiet days are healthy days.
- Some cards you'll reject. That's the system learning your taste — rejections
  cost nothing and delete their own PDFs.
- Your first "holy cow it named the company" moment, usually on card 2 or 3.

Tuning tip: exclusions beat keywords. "intern", "unpaid", "commission only"
remove more garbage than any keyword adds.

— The STPi desk
```

## Day 7 — activation nudge

```
Subject: your week in cards

Hi {{name}},

Your numbers: {{cards}} cards, {{approved}} approved, {{rejected}} rejected.

One thing worth 5 minutes: open the rejected cards and check WHY they were
rejected. If the match reasons read wrong, tighten min_relevance or add an
exclusion — 5 minutes now saves a week of noise.

And if a candidate got an interview, I'd genuinely like to hear about it.

— The STPi desk
```

## Day 29 — renewal (Whop renews automatically; this is the courtesy mail)

```
Subject: month 2 of STPi for {{tenant}}

Hi {{name}},

Month two begins tomorrow — {{price}} renews via Whop, same as month one.

Your month: {{cards}} cards, {{sends}} sends, {{hours_saved}} coaching hours
back (cards × 25 min of manual hunt-and-rewrite, our honest yardstick).

Change plan, pause, or cancel from your Whop library — no email required,
no retention call. We'd rather you stay because the cards are good.

— The STPi desk
```

## Day 45 — win-back (only if they cancelled)

```
Subject: the boards kept running

Hi {{name}},

No pitch. One honest line: the boards didn't stop posting when you paused —
PNet and CareerJunction alone move ~70 finance ads a week in Gauteng.

If the reason you left was noise, the fix is exclusions (5 minutes).
If it was price, tell me the number that works and I'll see what I can do.

Either way, your candidate files were never held hostage — they're YAMLs,
and they're yours.

— {{your_name}}
```

## Candidate-facing (forwarded by the coach)

```
Subject: Your job hunt just got a second pair of hands

Hi {{candidate}},

From this week, your job hunt runs on STPi:

- It checks the boards for you, once a day, Monday–Saturday.
- It shortlists only ads that match YOUR profile — location, field, seniority.
- It drafts a letter and CV per ad, tailored, never invented.
- NOTHING is ever sent without {{coach}} approving it first — and you can see
  every letter before it flies.

You keep doing the interviews. We'll keep doing the tabs.

— {{coach}}
```
