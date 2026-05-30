# Data Sources

All clinical seed data used in this assessment is sourced from publicly available medical guidelines and fictional hospital data created for demo purposes.

---

## Clinical Protocols

| Node | Source |
|------|--------|
| DVT prophylaxis post-op | NICE guideline NG89 — Venous thromboembolism in over 16s |
| Post-op vitals monitoring | Standard perioperative care guidelines (general medical knowledge) |
| TKR discharge rules | Standard orthopaedic surgical care guidelines |
| Sepsis Bundle v3 | Surviving Sepsis Campaign 2021 International Guidelines |
| Diabetic fasting protocol | Standard endocrinology practice guidelines |
| Contrast allergy pre-treatment | Standard radiology/ACR practice guidelines |
| Dual antiplatelet therapy | ESC/ACC cardiology guidelines |
| Antibiotic stewardship 72hr review | WHO AWaRe antibiotic guidelines |
| Blood transfusion two-person verification | NHS Blood Transfusion Safety guidelines |

---

## Drug Interactions

| Node | Source |
|------|--------|
| Warfarin-NSAID interaction | British National Formulary (BNF) + standard pharmacology |
| Penicillin cross-reactivity | NICE guidelines + standard allergy/immunology references |
| Paracetamol dosing | BNF standard adult dosing guidelines |

---

## Hospital Policies (Fictional — demo only)

The following data is entirely fictional, created specifically for this assessment:

- Bed capacity figures and expansion plans
- Nurse-patient ratios
- Vendor preferences (Zimmer Biomet, Smith & Nephew)
- Budget figures and salary restructuring data
- Patient records (Rajan, Padma, Aadhya) — fictional patients
- Staff names and designations
- NABH accreditation gap percentages

---

## Accreditation Standards

| Node | Source |
|------|--------|
| NABH accreditation criteria | National Accreditation Board for Hospitals & Healthcare Providers (India) |
| WHO hand hygiene 5 moments | World Health Organization — Hand Hygiene guidelines |

---

## Derivability Scores

Pre-computed scores (0.0–1.0) assigned manually based on this heuristic:
- Score > 0.7 = general medical knowledge an AI already knows (e.g. "What is DVT", "Paracetamol mechanism")
- Score < 0.7 = org-specific knowledge the AI cannot know without being told (e.g. "Supra uses Zimmer Biomet implants")

No LLM was used to compute derivability scores. All scores are pre-seeded in the database.