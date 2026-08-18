# Shared component / configuration architecture

```
vision/config/trust-first.ts          page configs + verified proof
vision/lib/trust-first.ts             variant + robots helpers
vision/app/preview/trust-first/       isolated routes + CSS
vision/app/components/trust-first/    presentation
vision/app/api/lead-preview/          preview form sink
```

One template: `TrustFirstLanding`. Ten page configs. Two variants (`simple`, `proof_heavy`) from the same markup. Proof-heavy shows extra modules; it does not change H1, URL, or intent.

Components: `CompanyHeader`, `TrustHero`, `EmployerQualificationForm`, `ProofStrip`, `RoleOrTaskCards`, `HowItWorks`, `WhyVirtualCoworker`, `EmployerComparison`, `CompanyProof`, `Testimonials`, `ObjectionHandling`, `FAQ`, `CompanyFooter`, `PreviewVariantToolbar`.

Toolbar is imported only by the preview layout and also refuses to render unless the path starts with `/preview/trust-first`.

Future production pages, if George ever approves them, should import the template without the toolbar and without `/preview` in the path. Paid-only production twins can stay `noindex` the way the competitor’s `/lp/` pages do. That decision is documented, not shipped.
