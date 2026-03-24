## Quick Product Launch Demo Design

### Goal
Ship a “quick product launch demo” path that mirrors the instant demo trigger but uses a lighter scenario so the entire flow (document injection, graph build, and simulation kick-off) completes in under two minutes. This gives visitors a low-friction, finishable experience while keeping the existing instant demo available for deeper scenarios.

### Composition
- **Demo source**: Reuse the front-end demo helper but add a new `quick launch` configuration that includes a single launch brief and a short list of social/analyst notes. Both files are plain text and small, so the upload + parsing step stays minimal.
- **LLM setup**: Point the quick demo at the same local/codex backend as the instant demo. Keep the `codex_cli` executable and omit API keys to favor the offline workflow already wired into the process page.
- **Trigger**: Add a second CTA button in the hero callout that imports and calls `getQuickProductLaunchDemoConfig`. The button loads the documents via `setPendingUpload` and navigates to `Process` in the same way as `runInstantDemo`, ensuring all downstream code paths remain unchanged.
- **Time override**: The quick demo stores `time_config_override` and `max_rounds_override` metadata so the backend can generate a compact config (shorter hours, smaller rounds) and cap the actual runner to fewer turns; this keeps the full experience under five minutes without touching the regular workflow.

### User experience
The hero section now shows two buttons: the existing “Run instant demo” that highlights a launch-day backlash narrative, and a new “Quick product launch demo” with a note stating it can finish within two minutes. Clicking the quick demo pre-fills the wizard form, loads the brief, and pushes to the simulation process. Because the new configuration only changes the `demo` payload, the same loading indicators, error handling, and pending-upload behavior apply.

### Testing & validation
- `npm run build` (frontend) to ensure the new import and button styles compile.
- Click both demo buttons locally to confirm each routes through `Process` with the expected documents and helper messages.
