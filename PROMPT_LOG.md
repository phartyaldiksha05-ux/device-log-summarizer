# PROMPT_LOG.md

## Initial prompt

"Write a Python script that reads a JSON list containing `device_id` and
`average_temperature`, then creates a Matplotlib bar chart comparing average
temperature by device. Include a chart title, axis labels, readable device
labels, and save the chart as a PNG."

## Issue found during review

The first draft used long device IDs on the x-axis without rotating the labels
or adjusting the layout. Labels could overlap or be cut off, making the chart
hard to read.

## Follow-up prompt

"Update the chart code to rotate x-axis labels, align them to the right, use
`tight_layout()` and save with `bbox_inches='tight'`. Add a y-axis grid, value
labels on each bar, and handle an empty JSON list without crashing."

## Review notes

- Added label rotation and `fig.tight_layout()` to reduce overlap.
- Added numeric labels above bars and axis labels/title.
- Added an empty-data message.
- Added file and JSON error handling.
- The sample chart is generated from `output.json`.
