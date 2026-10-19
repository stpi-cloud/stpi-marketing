# STPi — FAQ & objection handling

## FAQ

**Does it apply automatically?**
No. Every application requires a human tap on ✅. This is a design guarantee, not a
setting — there is no "auto" mode to turn on. STPi is a pipeline for your judgement.

**Will the AI invent experience on the CV or letter?**
No. The writer prompt hard-forbids inventing qualifications, employers, dates or skills;
it may only reorder and rephrase what is already on the profile. Ask for the sample CV
next to the sample letter and check line by line.

**Will I know if a candidate gets an interview?**
Yes. Employer replies go to the candidate and to your mailbox. STPi reads your mailbox
(read-only) and posts in #activity when an employer answers — interview invite, question,
no, or a bounced address — and a monthly report counts the interviews per candidate.
Interviews arranged only by phone won't show; ask candidates to tell you those.

**Will my (or my candidate's) Gmail get flagged as spam?**
Sends go out from your mailbox, to real ads, human-approved, with hard caps of 20 sends
per candidate and 150 per mailbox a day. A separate Gmail just for applications is best. That is the opposite of spray-and-pray.

**What happens to the data?**
The store keeps only `{job_url, status, timestamp}`. PDFs are deleted the moment a card
is sent or rejected, and untouched drafts self-delete after 72 hours. A candidate file
is a YAML — deleting the file is the right to erasure.

**Does it need my LinkedIn or scrape my profile?**
No LinkedIn login, no profile scraping. Public job search only.

**Which countries / boards?**
South Africa, Zimbabwe, Zambia, plus remote-first boards. 22 boards supported, 17 on by
default, including Adzuna, Google for Jobs (JSearch), PNet, CareerJunction, JobMail,
Bizcommunity, VacancyMail, iHarareJobs, JobsZimbabwe, GoZambiaJobs, Impactpool,
LinkedIn jobs search, Himalayas, Jobicy and Remotive. CVs render to
ZA, ZW and ZM conventions.

**What does it cost to run?**
The default deployment is two GitHub Actions workflows on a private repo: $0, no card,
no server to sleep. The customer brings their own free-tier LLM key and their own
mailbox (a Gmail app password — no Google Cloud project, no OAuth).

**What if a board blocks the runner or dies?**
Each hunter fails alone. The run reports "0 jobs" for that board and everything else
continues. One dead scraper never kills a hunt.

**I'm an agency — can we run our own?**
Yes: self-hosted mode on your own box, licence checked daily via a Cloudflare Worker.
On expiry it goes read-only — never bricked, never deletes your data.

**How do customers pay?**
Whop (card / PayPal / crypto, with affiliates), Lightning via coinos for ZW/ZM, or
Mukuru / cash as a manual grant. No other payment rails.

**How fast is onboarding?**
~10 minutes: a Discord webhook, a Gmail app password, one candidate YAML.

## Objections

**"AI cover letters are generic."**
Show the sample letter. Second paragraph names the company and mirrors two concrete
requirements; the facts trace back line-for-line to the CV. Generic is what *they*
were writing at 11pm — same letter, thirty employers. STPi writes a different letter
per ad because the match reason is per ad.

**"Mass applications get everyone blacklisted."**
Agree with them — then contrast: 20/day cap, human approval on every send, signed by the
candidate, to ads that passed a relevance threshold. "This isn't volume;
it's coverage. Every send is still a decision."

**"We already use an ATS / agency."**
An ATS is for employers; an agency is for sourcing. You're on the candidate's side.
STPi is the candidate-side desk. If anything, it feeds your ATS with better inputs.

**"My candidates won't trust a bot."**
The bot never talks to an employer. The employer receives a normal email signed by the
candidate ("Thandi Moyo via your practice"), their reply reaches the candidate directly, and every send needed a human tap first. The candidate sees
their own letter before it flies if they want to — the PDF is right there in the card.

**"It'll look like spam to employers."**
It's one application, to one real advert, signed by the candidate, with their
phone and signature. Read any of the samples aloud — it reads like a person because a
person approved it.

**"Why not just use ChatGPT myself?"**
You can — and then also maintain the board sweepers, the match scoring, the PDF
renderers for three countries, the expiry logic, the approval channel, and the 4am
cron. STPi is the difference between a prompt and a pipeline.

**"What's the catch with $0 hosting?"**
No catch, just honesty: GitHub Actions free tier is 2,000 minutes on a private repo;
illustratively, 5 minutes × 2 hunts/day × 26 days = 260 minutes/month for hunts alone.
Actual runs vary; outreach, press, retries and CI share the allowance. No blanket $0 bill
is promised. The customer's LLM key and mailbox have their own limits.
