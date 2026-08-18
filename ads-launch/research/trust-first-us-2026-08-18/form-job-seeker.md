# Form and job-seeker gating

## Preview form (implemented)

Fields: company name, your name, work email, US phone, role needed, optional company size, optional hiring timeline.

Employer language on the card. Visible diversion: “Looking for a job with Virtual Coworker?” → `https://virtualcoworker.com.ph` via `location.replace`.

US phone validation reused. Philippines mobiles get the careers message. Honeypot field is hidden.

POST `/api/lead-preview` only. Reuses `validateEmployerLead`. **Does not** call Zoho, send email, or fire `employer_inquiry_submitted`.

## What we did not do

Did not change live `GuidedMatchGate`. Did not global-block the words hire / hiring. Did not submit test leads into production Zoho.

## Ads negatives (document only — do not implement)

`job`, `jobs`, `salary`, `career`, `careers`, `apply`, `application`, `resume`, `work from home`.

Do not add `hire` or `hiring` as account negatives.
