type CsvColumn<T> = {
  key: keyof T;
  label: string;
};

function escapeCsvCell(value: unknown): string {
  const normalized = value == null ? "" : String(value);
  if (/[",\n]/.test(normalized)) {
    return `"${normalized.replace(/"/g, "\"\"")}"`;
  }
  return normalized;
}

// CSV export is intentionally generic so new services can reuse it later.
export function downloadCsv<T extends Record<string, unknown>>(
  filename: string,
  columns: CsvColumn<T>[],
  rows: T[],
): void {
  const header = columns.map((column) => escapeCsvCell(column.label)).join(",");
  const body = rows.map((row) =>
    columns
      .map((column) => escapeCsvCell(row[column.key]))
      .join(","),
  );
  const csv = [header, ...body].join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}
