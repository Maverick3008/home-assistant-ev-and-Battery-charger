# Release 1.5.0

## Multiple calendar support

- Select multiple Home Assistant calendars in the integration options.
- The earliest future event across all selected calendars is used for the charging plan.
- All selected calendars are refreshed every 30 minutes.
- Existing single-calendar configurations remain compatible.
- New diagnostic attribute: `calendar_entities`.
- `calendar_entity` continues to show the calendar that supplied the active event.
- Existing 100% / 80% calendar target-SOC behavior from 1.4.1 remains unchanged.
