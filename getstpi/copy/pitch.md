# STPi — pitches & positioning

Official tagline (README): **“Jobs found. Applications drafted. You tap approve. It sends.”**

---

## Elevator pitch (30 s)

STPi is a job-hunting copilot for career coaches in South Africa, Zimbabwe and Zambia.
It sweeps country-specific sources (keys and availability vary) on a schedule — PNet, CareerJunction, JobMail, VacancyMail,
iHarareJobs, GoZambiaJobs and more — matches every ad against your candidate's real profile,
scores the fit, then drafts a tailored cover letter and a country-formatted CV as PDFs.
The whole thing lands in your Discord as a single card with a ✅ and a ❌. Tap approve and it
sends the application from your mailbox, signed as the candidate. When the employer answers,
the reply reaches the candidate and you, and STPi flags interview invites. Nothing ever goes out without your tap.

## One-liner (15 s)

STPi finds the jobs, drafts the application, and waits for your tap. You stay the professional
in the loop; STPi does the forty-tabs part.

## Tweet-length

Your candidates aren't losing to better candidates. They're losing to the 40 open tabs.
STPi hunts, drafts, and asks before it sends.

## Positioning statement

For **career coaches, outplacement teams and job-search mentors in ZA / ZW / ZM** who lose
billable hours to board-by-board searching and letter rewriting, **STPi** is a
**human-in-the-loop application pipeline** that turns a private Discord channel into a
**deal-flow desk for job applications**. Unlike CV mass-mailers and AI “apply for me” bots,
STPi **never sends anything without approval, never invents a word of experience, and deletes
its own work product after 72 hours** — so you scale your judgement instead of outsourcing it.

## Stat block (verified, 2026-09-17, from production logs)

- 18 board integrations across ZA · ZW · ZM · remote; 11 returned live results on the latest run
- 41 drafted applications sitting in one Discord-linked pipeline, each with CV + letter PDFs
- ONE LLM call per job: score + letter + tailored CV (≈3× cheaper than score-then-draft)
- 0 auto-sends by design — every application is a human tap
- PDFs purged at 72 h; deleted the moment you send or reject
- $0 hosting: two GitHub Actions workflows, no server, no credit card
- 20 sends/day/candidate and 150/day/mailbox hard caps to protect your mailbox's reputation
- Reply alerts: interview invites, questions, no's and bounces flagged in Discord; monthly interview report

## Don't say

- “AI applies for you” (we don't — a human approves every send; saying otherwise is false and
  invites Gmail abuse questions)
- “guaranteed interviews” (no such thing; we sell hours saved and coverage, not outcomes)
- “scrapes LinkedIn” (we don't log in or scrape profiles; public job search only)
- “unlimited applications” (we deliberately cap volume; quality-over-spam is the pitch)
