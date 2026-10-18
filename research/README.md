# Research is an eligibility gate, not a send-approval queue

Cold STPi sales outreach remains automatic. Candidate applications alone require a tap.
The machine may queue cold outreach only for a lead with two current, distinct public
research signals in `lead-evidence.json`. Missing evidence is not permission to fabricate it.
The registry starts empty deliberately: no real prospect evidence has been verified in this
repair session. This blocks generic cold mail when the review changes are adopted.

Each `leads` entry is keyed by the existing lead-store ID (never an email address):
`{"signals":[{"url":"https://public-source.example/service","quote":"Exact observed service statement, not an inference.","checked_at":"2026-10-16T12:00:00Z"}, ...]}`.
Two distinct quotes, 20–220 characters each, checked within 30 days, are required. They may
come from one public page if they establish different facts. Quotes must be checked against
the cited pages by the research process; schema validation is NOT fact verification.
Do not put private messages, scraped personal contacts or invented prospect pain in this file.
No links inside quotes: first touch has exactly one CTA (the free downloadable demo).

Release blocker: populate real evidence and connect a bounded, safe research collector before
expecting automatic cold-mail volume. No collector was run and no lead was modified here.
Previously queued mail without evidence moves to `research_hold`, not sent. After evidence is
added, compose automatically re-renders those held rows using current copy before resuming.
Human replies suppress queued/held mail; automatic replies pause it for operator handling.
