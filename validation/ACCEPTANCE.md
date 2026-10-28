# Additional acceptance review

PASS for numerical score reproducibility: all 1,409 holdout scores match independent logistic-equation calculations to floating-point precision. LIMITED for prediction use: subgroup ROC-AUC ranges from 0.709 to 0.887. Overall ROC-AUC must not be represented as uniform performance. The two-year group has only nine positive outcomes, so its ranking estimate is particularly uncertain. These diagnostics do not establish an effective intervention or suitability for a new customer population.

Reproduce with `python validation/acceptance.py`. Results are in `validation/results.json`.

Status: local validation only. Container startup, deployed UI behavior, deployment revision mapping, and live source-link checks remain outstanding. No live service has been updated.
