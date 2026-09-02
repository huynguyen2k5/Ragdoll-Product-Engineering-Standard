# UI Context

## Status

{{UI_STATUS}}

Use one of:

- `APPLICABLE`
- `NOT_APPLICABLE`
- `UNDECIDED`

If the project has no user interface, set `NOT_APPLICABLE` and do not invent a design system.

## Product / Design Intent

{{DESIGN_INTENT}}

## Theme

{{THEME_DESCRIPTION}}

## Semantic Color Tokens

| Role | Token / Variable | Value |
| --- | --- | --- |
| Page background | `{{BG_BASE_TOKEN}}` | {{BG_BASE_VALUE}} |
| Surface | `{{BG_SURFACE_TOKEN}}` | {{BG_SURFACE_VALUE}} |
| Primary text | `{{TEXT_PRIMARY_TOKEN}}` | {{TEXT_PRIMARY_VALUE}} |
| Muted text | `{{TEXT_MUTED_TOKEN}}` | {{TEXT_MUTED_VALUE}} |
| Primary accent | `{{ACCENT_TOKEN}}` | {{ACCENT_VALUE}} |
| Border | `{{BORDER_TOKEN}}` | {{BORDER_VALUE}} |
| Error | `{{ERROR_TOKEN}}` | {{ERROR_VALUE}} |
| Success | `{{SUCCESS_TOKEN}}` | {{SUCCESS_VALUE}} |

Use project tokens rather than arbitrary one-off colors. Remove the table when UI is not applicable.

## Typography

| Role | Font / Stack | Token |
| --- | --- | --- |
| UI text | {{UI_FONT}} | `{{UI_FONT_TOKEN}}` |
| Code/mono | {{MONO_FONT}} | `{{MONO_FONT_TOKEN}}` |

## Spacing and Radius

- Spacing scale: {{SPACING_SCALE}}
- Radius scale: {{RADIUS_SCALE}}

## Component Library

{{COMPONENT_LIBRARY_OR_STRATEGY}}

Record whether components are generated, vendor-owned, or project-owned, including protected/generated paths.

## Layout Patterns

- {{LAYOUT_PATTERN_1}}
- {{LAYOUT_PATTERN_2}}

## Interaction States

Design applicable components for:

- default;
- hover;
- active/pressed;
- focus;
- selected;
- loading;
- empty;
- error;
- success;
- disabled;
- permission-restricted;
- long/overflowing content;
- offline/unavailable when relevant.

## Icons

{{ICON_SYSTEM}}

## Accessibility

- Contrast: {{CONTRAST_REQUIREMENT}}
- Keyboard/focus: {{KEYBOARD_FOCUS_REQUIREMENT}}
- Touch targets: {{TOUCH_TARGET_REQUIREMENT}}
- Reduced motion: {{REDUCED_MOTION_REQUIREMENT}}
- Additional requirements: {{ACCESSIBILITY_REQUIREMENTS}}

Do not communicate important state by color alone.

## Responsive Behavior

{{RESPONSIVE_RULES}}

## Design Assets / References

- {{DESIGN_REFERENCE_1}}

## Context Provenance

- **OBSERVED:** {{OBSERVED_UI_EVIDENCE}}
- **DECLARED:** {{DECLARED_UI_EVIDENCE}}
- **INFERRED:** {{INFERRED_UI_EVIDENCE}}
- **UNDECIDED:** {{UNDECIDED_UI_ITEMS}}
