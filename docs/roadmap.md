# Roadmap

The roadmap is intentionally small and evidence-driven. New features should
come with a reproducible example and a validation reference.

## Near term

- add tabulated cable definitions with unit-aware input validation;
- add optional temperature and elastic-stretch corrections;
- add a CSV export command for sampled span results;
- publish worked examples for level, unequal-elevation, and wind-load cases.

## Later

- provide a lightweight plotting extra without making plotting a runtime
  dependency;
- add a multi-span string model with explicit assumptions;
- compare selected cases with independent reference calculations;
- document interoperability with finite-element workflows.

## Out of scope for the first releases

- replacing a utility's governing design code;
- hiding uncertainty behind a single safety factor;
- bundling proprietary cable libraries or project data.
