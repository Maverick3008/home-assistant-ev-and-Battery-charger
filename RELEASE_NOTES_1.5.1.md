# Release 1.5.1

## Simple 03:00 calendar fallback

This release adds a simple charging safety fallback for cases where the vehicle SOC does not update correctly.

- From **03:00**, if a future calendar event still exists later today and the normal charging plan is `not_needed`, the integration switches the charge-plan status to **`charging_window`**.
- The fallback ignores SOC.
- `planned_start` becomes **03:00**.
- `planned_end` becomes the start of today's next calendar event.
- The displayed charge duration is the complete fallback window and is not SOC-based.
- The fallback automatically ends when the event starts.
- New diagnostics:
  - `calendar_fallback_active`
  - `calendar_fallback_reason`
  - `calendar_fallback_start`
- Multiple-calendar support from 1.5.0 remains unchanged.

Recommended GitHub tag: `1.5.1`
