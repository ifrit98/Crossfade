# PRD checklist

A PRD includes the sections that apply and a reviewer asks about the ones missing. Not every slice needs every section; a three-person team that must fill ten sections stops writing PRDs.

- **Header:** id, status, owner, reviewers, dependencies, contracts touched, invariants enforced, size budget.
- **Outcome:** one sentence, the user's end-to-end action and what they observe.
- **Scope and non-goals:** what is built, what is mocked, what is provisional. A research slice separates the scientific claim from the software deliverable.
- **Functional requirements:** stable ids, one testable obligation each, each mapped to an invariant or marked as none.
- **Acceptance tests:** given / when / then, with ids that map to pytest names `test_<slice>_atNN_<slug>`.
- **Implementation increments:** ordered, each ending in a runnable test.
- **Definition of done:** tests, budget, demo, and the sentence that says what the slice does not claim.
- **Open inputs:** each with who resolves it and what it blocks.
