# Human questions — 13 August 2026

Do not ask a person something the APIs or code already answered.

Ask these. Stop. Wait.

---

## Caitlin

You own this CRM day to day.

1. When a real employer becomes a job order, is the object we should care about the **Job Orders** list — not the Sales Enquiry status **Job Order Submitted**? (Those counts were 242 vs 213 in 90 days, so they are not the same thing.)
2. Is the old Zapier “tell Google Ads a job order happened” path **still on**? If you don’t have Zapier, who does?
3. Who or what is the Zoho user **Social Marketing, Lois**? What process creates Website rows under that name?
4. Looking at these recent job-order companies (names only): Real Advantage Title, Safeco, Rain City Fence, Waterlily Exercise Physiology, Foxlaw, TDE, Box&Go Moving, Collectively Corp, Lumiriam, Kim4Kids, MB Brick and Block Laying — which of these are real hiring clients you would ever want advertising to learn from, and which are tests or already dead?
5. Where does “signed” live? Is it a contract in Zoho Sign, `Contract_Invoice_Status` on Placements, or something outside Zoho?

---

## Cheyenne

US sales and the US Calendly page.

1. When an employer submits the new site (`virtualcoworker.app/us`), do you get an email you can actually work — and can you tell it apart from the old website leads?
2. After a useful call on **888-964-8644**, do you create a Sales Enquiry, or does that only happen if they already filled a form?
3. Who answers that line, and who gets the missed calls?
4. Is **Social Marketing, Lois** a person you work with, a shared mailbox, or the name the website uses when it drops leads in?

---

## Holly

AU sales.

1. Same as Cheyenne for `virtualcoworker.app/au` and **1300 886 740**: do `.app` leads arrive, and who answers the phone?
2. For Australia, is Region **AU** on the enquiry enough, or do you also need something else to treat it as your lead?

---

## Raffie

Technical / Zapier / GTM.

1. Is there a live Zap (or Zoho Flow) that still uploads to Google Ads conversion actions named **Zoho JO Submitted** or **Standard OCI**? On or off, US and AU.
2. In GTM, is `employer_inquiry_submitted` mapped once to `VC_US_Thank_You` — and **not** also to `form_submit_success` or a thank-you page view?
3. Is Calendly **invitee created / event scheduled** mapped anywhere, or only the overlay open?
4. Does anyone still have the old Zap field map (which Zoho status fired the upload, which click-id field, which Ads action)?

If you cannot get into Zapier, say so. A screenshot of the Zaps list is enough. Do not turn anything back on.

---

## Amanda

Google Ads side.

1. On `VC_US_S_CORE`, `VC_US_S_ROLES`, `VC_AU_S_CORE`, `VC_AU_S_ROLES`, are campaign-specific goals limited to the new pipe checks — or is the account default basket still attached?
2. Please do **not** recommend Broad, Performance Max, DSA, or Maximize Conversions for this cold start. The ask is: are the new thank-you / 60s-call / Calendly-booked actions actually eligible on those campaigns, and is anything museum-shaped still eligible?
3. If we ever test **one** offline row later, it must be a **new Secondary** action, not the old Zapier twins. Do you agree that those twins stay museum-only?

---

## Do not ask them

- How many Leads are in Zoho (we know: Sales Enquiries = 3,433).
- Whether `.app` writes to Zoho (it does not).
- Whether `utm_gclid` exists (it does).
- Whether Brand should be enabled (deferred).
- For passwords, tokens, or to authorize a new connector from chat.
