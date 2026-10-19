# I treat job applications as a pipeline, not a resume problem

_Published on dev.to (owner persona), mirrored on Nostr. Archived here verbatim, fetched 2026-10-01._

Every piece of career advice still assumes the bottleneck is the document. Polish this, quantify that, beat the ATS parser with the right keywords. None of it disputes that the words matter. All of it ignores that most applications never reach a human because of where and when they were aimed, not what they said.

Here is the failure order I keep observing, roughly in order of damage:

1. The role was wrong for you and you knew it, but a blank Sunday said otherwise.
2. The application went out four to nine days after posting, into a pile of hundreds.
3. The letter was generically excellent and specifically empty, so the reader felt the form letter.
4. Only then, maybe, does a parser or a recruiter glance at the resume itself.

A CV tweak fixes item three at best. The real fix is operational: treat the search as a small production system with sourcing, screening, drafting and a quality gate. This post is about the one I built and run for other people, stpi, and specifically the architecture, because the architecture is the part worth stealing even if you never touch my code.

## The nightly hunt

A scheduler (in our case free GitHub Actions, four in the morning local time) walks a configured set of sources: PNet, Careers24, PiH, the PSVAC government gazette, LinkedIn's public job search, and a few niche feeds. Each source is a scraper plus an adapter, because there is no other honest word for it: the gazette is unstructured PDF, one board blocks bots at the edge (which incidentally protects legitimate small pipelines from the four-hundred-application crowd), another returns RSS, another a JSON API pretending to be a website.

The interesting part is what happens on nights with zero results. Zero is not a bug report, it is market data: global remote boards genuinely rarely pay off for a Harare or Johannesburg profile, and a pipeline that measures that lets you stop taking it personally. We log every source's yield and it changes how people aim.

## Scoring against a truth file

Every candidate role gets scored against two documents: the CV, and what we call the truth file. The truth file is a short list of verified facts: projects, dates, numbers, technologies, contexts. Its whole purpose is negative: the model may only cite what appears there. If it is not in the truth file, it does not exist for the application.

This is the single most underrated control in any LLM drafting system. Not tone, not temperature. Provenance. A drafter constrained to a truth file produces boring, checkable prose, and boring prose that survives a reference call beats confident prose that does not. Our scorer also learns, gently: when a candidate taps "no" on an approval card, the reason codes feed back into ranking, so the same category of bad fit comes back less often.

## The queue, and the brake

Drafted applications land as interactive cards on Discord (or Telegram): role, company, salary if posted, the fit score with reasons, and a preview of the letter. Each card has exactly the actions you would want to exist: approve and send at the scheduled time, edit the draft, reject with a reason, snooze.

Nothing sends without a yes. That rule is not a disclaimer, it is the design. Every auto-apply product I have seen fails the same way: it optimises volume, reply rates collapse, sender reputations burn, and the human stops reading their own applications. A pipeline that sends on your behalf without a gate is not a job-search tool, it is a reputation destroyer with good marketing. The approval step is where your judgment enters the loop, and judgment is what the market actually pays for.

Caps are enforced in software, not in promises: candidates per night, sends per month, usage counters persisted on disk next to the state, and the machine simply stops and asks when a cap is hit. Demo builds get small caps; paid tiers raise them; nobody gets a surprise invoice from a runaway agent because runaway is not representable in the system.

## Why it runs on your infrastructure

The whole thing is a Python package plus a repo with a scheduler. The data plane (CVs, truth files, queue state) lives in your GitHub repo or your own box; the only third party it talks to is the LLM provider you choose, and a failover chain of them, so one provider's rate limit does not starve a hunt mid-run. There is no account to make with us, no database of your candidates sitting on someone else's server, and when you stop paying, the pipeline keeps running because it was never hosted by us in the first place. That is also why payment is honour-based: the hosted service is convenience, the capability is yours.

## What I would tell you to copy

If you would rather build your own, and honestly you should if this is your day job, steal the shape:

- Measure source yield nightly and let zero-days retarget you.
- Constrain the drafter to a provenance document. Boring beats brilliant.
- Freshness beats fit: submit within hours of posting or do not bother.
- Keep a human on the trigger and put the caps in code.
- Log every rejection as training data; your no is smarter than your yes.
- Run it where your data lives. Automation that needs you to trust a stranger's database will eventually give you a reason not to.

The machine is a small factory with one employee and one quality gate, and the gate is you. Everything else is plumbing, and the plumbing is the part you are allowed to buy.
