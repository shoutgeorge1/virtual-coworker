# Keyword demand table

**Planner fields (US volume, 3-mo, YoY, competition, top-of-page bids): not available.** No Ads developer token / Keyword Planner client in this environment.

What we do have is account search-term evidence (Editor ST export ~2024-08-01 to 2026-08-04). Combined USA+AU from `ads-launch/_evidence_search_terms.json` unless noted. Ads conversions ≠ qualified employers.

| Keyword | US+AU clicks | Cost | Ads conv | Intent | Employer vs job-seeker | Match | Ad group | Launch |
| --- | ---: | ---: | ---: | --- | --- | --- | --- | --- |
| virtual marketing assistant | 84 | 2152 | 6.0 | Hire a marketing VA | Employer | Exact + Phrase | Digital_Marketing_VA_PH | LAUNCH NOW |
| social media manager philippines | 81 | 2451 | 6.0 | PH SMM hire | Employer (title is “manager”) | Keep in existing Hire group | Social_Media_Hire_PH (unchanged) | Existing, paused |
| social media virtual assistant | 49 | 1346 | 3.2 | Core social VA | Employer | Exact + Phrase | Social_Media_VA_PH | LAUNCH NOW |
| social media assistant | 73 | 1089 | 1.0 | Generic assistant | Ambiguous | Do not add | — | Skip (weak) |
| virtual social media assistant | 28 | 806 | 4.0 | Social VA wording | Employer | Exact + Phrase | Social_Media_VA_PH | LAUNCH NOW |
| social media va | 28 | 1002 | 1.0 | Short head | Mixed | Exact only | Social_Media_VA_PH | LAUNCH NOW |
| virtual assistant social media | 26 | 509 | 3.0 | Word-order variant | Employer | Exact + Phrase | Social_Media_VA_PH | LAUNCH NOW |
| filipino social media manager | 19 | 631 | 3.0 | PH SMM | Employer | Existing Hire group | Social_Media_Hire_PH | Existing |
| marketing va | 18 | 639 | 2.0 | Short head | Mixed | Exact only | Digital_Marketing_VA_PH | LAUNCH NOW |
| digital marketing philippines | 20 | 929 | 3.0 | Geo + function | Ambiguous (agency / hire mix) | Existing Hire/Outsource | Digital_Marketing_Hire_PH | Existing |
| digital marketing virtual assistant | 13 | 437 | 1.0 | Core marketing VA | Employer | Exact + Phrase | Digital_Marketing_VA_PH | LAUNCH NOW |
| social media management philippines | 12 | 455 | 2.0 | PH management | Employer-leaning | Existing | Social_Media_Hire_PH | Existing |
| hire philippines social media manager | 10 | 436 | 2.0 | Hire + PH | Employer | Existing | Social_Media_Hire_PH | Existing |
| lead generation virtual assistant | 11 | 331 | 5.3 | Lead-gen VA | Employer, **sales** not LinkedIn | Existing Sales group | Sales_Hire_PH | Do not move |
| digital marketing outsourcing philippines | 4 | 161 | 0 | Outsource | Employer-leaning, no conv | Existing Outsource | Digital_Marketing_Outsource_PH | Existing |
| social media virtual assistant jobs | — | — | — | Jobs | **Job seeker** (USA ST waste list) | Negative (already covered by Broad `jobs`) | — | Block |
| instagram virtual assistant | none in ST export | — | — | Platform VA | Likely employer, unproven volume | Exact + Phrase, folded | Social_Media_VA_PH | TEST LIGHTLY |
| linkedin virtual assistant | none in ST export | — | — | Platform VA | Unknown / lead-gen bleed | — | — | DO NOT LAUNCH |
| facebook / tiktok / youtube / pinterest VA | none in ST export | — | — | Platform VA | Thin; Pinterest = training risk | — | — | DO NOT LAUNCH |
| tiktok shop virtual assistant | none in ST export | — | — | Ecommerce operator | Interesting, unproven | — | — | DO NOT LAUNCH |

USA-only slices that matter (`historical-performance-summary.json`):

| Search term | Impr | Clicks | Cost | Conv | Class |
| --- | ---: | ---: | ---: | ---: | --- |
| social media manager philippines | 221 | 44 | 1155 | 3.0 | employer_intent_keep |
| filipino social media manager | 66 | 17 | 547 | 1.0 | employer_intent_keep |
| digital marketing philippines | 91 | 10 | 410 | 1.0 | employer_intent_keep |
| social media manager for hire | 250 | 14 | 335 | 1.0 | employer_intent_keep |
| hire a social media manager | 86 | 7 | 326 | 1.0 | employer_intent_keep |

Adjacent Planner-style discovery: **not run**. Do not invent US monthly volumes.
