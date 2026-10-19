# Publish nothing you would not want opened on a projector

_dev.to 2026-09-30 · tags: career, interview, portfolio · https://dev.to/simali_dud_b97add4154d7a6/publish-nothing-you-would-not-want-opened-on-a-projector-4952 — archived via dev.to API 2026-10-01._

## Every linked artifact is an interview waiting to happen

When you open a portfolio, a recruiter is not looking for a polished show‑case.  
They are looking for evidence of a workflow that can be trusted, of decisions that can be defended, and of a culture of continuous delivery.  
In that sense, every link you expose on your résumé becomes a scheduled interview slot.  
It is a cue to a conversation, and the content of the link must be ready to answer the questions that will come next.

---

## Half‑finished demos teach them you ship half‑finished

The first rule of portfolio engineering is to publish early.  
A demo that is incomplete is still a demo.  
It signals that you are willing to expose your work, that you accept feedback, and that you ship on schedule.  
When a recruiter sees a demo that is still under development, they see an engineer who can iterate quickly, who can surface issues, and who can push a minimal viable product to the next milestone.

Avoid the temptation to perfect every line of code before sharing.  
Your goal is to demonstrate the value of the feature, not to exhibit a flawless code base.  
If a demo is only half‑finished, make that explicit in the description:  
“Version 0.5, shipping the core feature; polishing pending.”  
This turns the demo into a live case study of an engineering sprint, of backlog grooming, of a realistic delivery window.

---

## A tiny repo with a README that explains decisions outscores a big one that does not

Size is not a metric of impact.  
A 500‑line repository that documents why a particular algorithm was chosen, how the trade‑offs were evaluated, and how the design aligns with product goals speaks louder than a 10,000‑line monolith that offers no context.  
The README is the first thing a recruiter reads.  
It is a written interview where you narrate the problem, the solution, and the rationale.

A concise README should contain:

* **Problem statement**, what business need or technical constraint prompted the work  
* **Solution overview**, a high‑level sketch of the architecture and key components  
* **Decision record**, why you chose this approach over alternatives, citing trade‑offs in performance, maintainability, or cost  
* **Testing strategy**, a brief outline of unit tests, integration tests, and coverage metrics  
* **Next steps**, what would you change if you had more time, or what is on the roadmap

If a repository is large but the README is empty, the recruiter is left guessing.  
They will see that the code exists, but they cannot assess whether the engineering choices were sound.  
By contrast, a small repo with a thoughtful README demonstrates the same depth of thought in a more efficient way.

---

## If it would embarrass you in the room, pull it now

A portfolio is a curated set of artifacts, not a museum of every commit ever made.  
Anything that reveals a learning curve, a debugging session that ended in failure, or a code smell that you later refactored is a signal that you learn from mistakes.  
However, if an artifact contains a mistake that you could not correct, or if it shows a misunderstanding of fundamental concepts, it is better to remove it.

Think of the portfolio as a “show room.”  
Just as a real‑estate agent will not display a property that needs a new roof, you should not expose a code base that still uses a deprecated API or a hard‑coded path that you know is a security risk.  
Pulling such artifacts is not a sign of weakness; it is a disciplined choice to keep the narrative clean and focused on the value you bring.

When you remove an embarrassing piece, replace it with a lesson.  
A comment in the code or a short note in the README that explains how the issue was identified and fixed can become a talking point in an interview.

---

## The mechanics of a clean portfolio

1. **Track what you publish**, keep a simple spreadsheet that lists each link, the date added, the status (demo, repo, blog), and the last updated date.  
   This gives you visibility into how frequently you add new content and how long artifacts remain stale.

2. **Apply the 30‑day cooldown**, after you submit a job, give each role or employer a 30‑day window before you reapply.  
   The same rhythm applies to the portfolio: if a project has not been touched or updated in 30 days, consider it for removal or rework.

3. **Human approval gate**, before any link is made live, run it through a quick checklist: does it compile? does it run? is the README clear?  
   No link should be shared without a final click.

4. **Automate reminders**, set up a cron job that emails you every month with a reminder to review each artifact, to note any that have become outdated, and to plan an update if necessary.

5. **Keep the voice consistent**, the tone of your README and demo description should mirror your personal brand: clear, concise, and technically grounded.  
   Avoid jargon that might be misread and steer clear of buzzwords that dilute credibility.

---

## Why the focus on artifacts matters

Recruiters, career coaches, and hiring teams are pressed for time.  
They scan a portfolio to decide whether to schedule a deeper conversation.  
If every link they follow is an interview in miniature, they will see patterns: how you think, how you solve problems, and whether you fit the team culture.

When you publish a demo that is intentionally incomplete, a recruiter learns that you are comfortable iterating.  
When you expose a tiny repo with a thoughtful README, they see that you can communicate complex ideas in simple words.  
When you remove an embarrassing artifact, they learn that you are self‑aware and proactive.

All these signals are measurable.  
They can be tracked as part of your personal operations: number of links added, number of updates per quarter, average time from commit to demo release.

---

## A brief note on tooling

If you need a lightweight system to manage these artifacts, consider a self‑hosted solution that gives you full control over when and how content is shared.  
It can automate the approval gate, enforce your 30‑day cooldown rule, and track the metrics that matter for a disciplined engineering workflow.

*Try the demo zip at https://getstpi.pages.dev/downloads/stpi-demo-1.0.2.zip and see how a simple, open‑source tool can keep your portfolio as clean and operational as your code.*