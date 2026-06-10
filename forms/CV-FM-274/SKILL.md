# CV-FM-274 — Referee's Case Management Conference Order

**Form Number:** CV-FM-274
**Fillable Fields:** 125
**Category:** Civil/Family — Referee Program
**Court:** Superior Court / District Court
**Related Forms:** CV-FM-270

## Purpose

Court-paid referee's order after case management conference, documenting case type, attendees, contested issues, discovery schedule, and hearing logistics.

## Governing Law

- **Administrative Order JB-22-03**

## Field Mapping Summary

### Page 0

| Field Name | Type | Source |
|-----------|------|--------|
| `Plaintiff` | Text | From matter data |
| `Defendant` | Text | From matter data |
| `Other party` | Text | From matter data |
| `Superior Court` | CheckBox | `matter.court_type` |
| `District Court` | CheckBox | `matter.court_type` |
| `County` | Text | `matter.court_county` |
| `Location Town` | Text | `matter.court_location` |
| `Docket No` | Text | `matter.docket_number` |
| `plaintiff` | CheckBox | From matter data |
| `by telephonevideo` | CheckBox | `party.phone` |
| `plaintiffs attorney` | CheckBox | From matter data |
| `After notice to the parties the referee held a case management conference with the parties The following were present` | Text | From matter data |
| `by telephonevideo_4` | CheckBox | `party.phone` |
| `defendant` | CheckBox | From matter data |
| `by telephonevideo_2` | CheckBox | `party.phone` |
| `defendants attorney` | CheckBox | From matter data |
| `undefined` | Text | From matter data |
| `by telephonevideo_5` | CheckBox | `party.phone` |
| `DHHS` | CheckBox | From matter data |
| `by telephonevideo_3` | CheckBox | `party.phone` |
| `AAG` | CheckBox | From matter data |
| `1` | Text | From matter data |
| `by telephonevideo_6` | CheckBox | `party.phone` |
| `GAL` | CheckBox | From matter data |
| `2` | Text | From matter data |
| `by telephonevideo_7` | CheckBox | `party.phone` |
| `Other` | CheckBox | From matter data |
| `undefined_2` | Text | From matter data |
| `by telephonevideo_8` | CheckBox | `party.phone` |
| `divorce` | CheckBox | From matter data |
| *... +49 more fields* | | |

### Page 1

| Field Name | Type | Source |
|-----------|------|--------|
| `Civil` | CheckBox | From matter data |
| `1_2` | Text | From matter data |
| `SETTLEMENT CONFERENCE The parties shall send the referee and exchange with each other settlement` | CheckBox | From matter data |
| `3 business days` | CheckBox | From matter data |
| `The settlement proposal should reflect a good faith attempt to resolve the matter At the settlement conference` | CheckBox | From matter data |
| `before the settlement conference` | Text | From matter data |
| `HEARING` | CheckBox | From matter data |
| `Witnesses and Exhibits Number of plaintiffs witnesses` | Text | From matter data |
| `defendants witnesses` | Text | From matter data |
| `GALs witnesses` | Text | From matter data |
| `other partys witnesses` | Text | From matter data |
| `14 days before the hearing or` | CheckBox | From matter data |
| `by mmddyyyy` | CheckBox | From matter data |
| `undefined_8` | Text | From matter data |
| `7 days before the` | CheckBox | From matter data |
| `by mmddyyyy_2` | CheckBox | From matter data |
| `undefined_9` | Text | From matter data |
| `no later than 7 days before the hearing` | CheckBox | From matter data |
| `by mmddyyyy_3` | CheckBox | From matter data |
| `Submission of Exhibits to Referee The parties shall email copies of exhibits to the referee in PDF format` | Text | `party.email` |
| `at the` | CheckBox | From matter data |
| `In addition to emailing the exhibits to the referee the parties shall send paper copies of all exhibits to` | CheckBox | `party.email` |
| `the referee at` | Text | From matter data |
| `7 days or` | CheckBox | From matter data |
| `format except that proposed child support orders and worksheets may be sent as an editable PDF no later` | CheckBox | From matter data |
| `days before the scheduled hearing` | Text | From matter data |
| `Estimated length` | Text | From matter data |
| `Date of settlement conferencehearing mmddyyyy` | Text | `today()` or relevant date |
| `at` | Text | From matter data |
| `am` | CheckBox | From matter data |
| *... +7 more fields* | | |

### Page 2

| Field Name | Type | Source |
|-----------|------|--------|
| `The hearing will be held remotely and thus the court will arrange and pay for the recording` | CheckBox | From matter data |
| `The hearing will be held in person and thus the parties will arrange and pay for private court reporting` | CheckBox | From matter data |
| `undefined_10` | Text | From matter data |
| `Text1` | Text | From matter data |
| `OTHER 1` | Text | From matter data |
| `Text5` | Text | From matter data |
| `Date mmddyyyy` | Text | `today()` or relevant date |
| `undefined_11` | Text | From matter data |
| `Text2` | Text | From matter data |


## AI Hints

125 fields — very complex, 3-page form. Completed by referee, not parties. Documents: attendees (with telephone/video indicators), case type (divorce, parental rights, parentage, modification, contempt, enforcement, PFA, etc.), contested issues, proposed exhibits, witnesses, discovery deadlines, hearing dates, and special requirements.

## Validation Checklist

- [ ] Case caption is complete (parties, court, docket number)
- [ ] Correct court type selected (Superior/District)
- [ ] Related forms prepared if needed (CV-FM-270)
