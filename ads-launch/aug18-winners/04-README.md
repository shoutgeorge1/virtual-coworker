# File 04 — paused challenger ads (after 02)

Not today’s Post. Import only after Australia file `02` is Posted.

## Files

- `04-spend-only-challengers-us.csv` — 16 Paused RSAs
- `04-spend-only-challengers-au.csv` — 12 Paused RSAs
- Look first: https://vc-xray.vercel.app/aug18-next.html

## Rules

- All Ad Status = Paused. Campaign and ad group status are blank so Editor does not pause live groups.
- If a group already has 3 enabled RSAs, this is a paused extra. Do not Enable a 4th.
- Frozen groups are not in these files: US `Hire_VA_PH`, AU `Social_Media_Hire_PH`.
- Brand is not in these files.
- Final URLs stay on the existing hub or role page. Frozen paths unchanged.
- Do not mix with file 02.

Rebuild: `python3 ads-launch/aug18-winners/build_spend_only_challengers.py`
