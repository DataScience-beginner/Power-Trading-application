import { useState } from "react";
import { downloadCsv } from "../lib/export";
import { uploadWorkbook } from "../lib/api";
import { getStoredSession } from "../lib/authStorage";
import type { WorkbookUploadResponse } from "../lib/types";

type UploadWorkbookPanelProps = {
  onUploaded?: (workbookId: string) => void;
};


// This panel keeps the first workbook flow self-contained while the client dashboard grows.
export function UploadWorkbookPanel({ onUploaded }: UploadWorkbookPanelProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [result, setResult] = useState<WorkbookUploadResponse | null>(null);
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleUpload() {
    const session = getStoredSession();
    if (!session) {
      setError("Please sign in before uploading a workbook.");
      return;
    }
    if (!selectedFile) {
      setError("Select an .xlsx workbook first.");
      return;
    }

    setError("");
    setIsSubmitting(true);
    try {
      const uploadResult = await uploadWorkbook(session.token, selectedFile);
      setResult(uploadResult);
      onUploaded?.(uploadResult.workbook_id);
    } catch (requestError) {
      setError(
        requestError instanceof Error ? requestError.message : "Upload failed.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="panel upload-panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Workbook Ingestion</p>
          <h3>Upload Monthly Source File</h3>
        </div>
        <span className="status-badge status-badge-accent">xlsx only</span>
      </div>

      <p className="muted">
        Supports the current Excel format with `DAM`, `RTM`, `TNEB`, and legacy
        `Solar Working` totals used as a temporary solar source.
      </p>

      <div className="upload-grid">
        <label className="field upload-dropzone">
          <span>Workbook file</span>
          <input
            accept=".xlsx"
            onChange={(event) =>
              setSelectedFile(event.target.files?.[0] ?? null)
            }
            type="file"
          />
          <strong>{selectedFile?.name ?? "Drop or browse workbook"}</strong>
          <small>Expected sheets: DAM, RTM, TNEB, future Solar.</small>
        </label>

        <div className="upload-actions">
          <button
            className="primary-button"
            disabled={isSubmitting}
            onClick={handleUpload}
            type="button"
          >
            {isSubmitting ? "Processing..." : "Upload and calculate"}
          </button>

          <div className="detail-list compact-detail-list">
            <div>
              <span>Submission</span>
              <strong>{isSubmitting ? "Running" : "Ready"}</strong>
            </div>
            <div>
              <span>Latest Output</span>
              <strong>{result?.status ?? "Not started"}</strong>
            </div>
          </div>
        </div>
      </div>

      {error ? <p className="error-text">{error}</p> : null}

      {result ? (
        <div className="result-block upload-result-block">
          <div className="result-summary-grid">
            <article>
              <span>Workbook</span>
              <strong>{result.file_name}</strong>
            </article>
            <article>
              <span>Status</span>
              <strong>{result.status}</strong>
            </article>
            <article>
              <span>Month</span>
              <strong>{result.workbook_month ?? "unknown"}</strong>
            </article>
            <article>
              <span>Calculated Rows</span>
              <strong>{String(result.calculation_summary.row_count ?? 0)}</strong>
            </article>
          </div>

          <div className="table-wrap" style={{ marginTop: "1rem" }}>
            <table className="data-table compact-table">
              <thead>
                <tr>
                  <th>Sheet</th>
                  <th>Type</th>
                  <th>Status</th>
                  <th>Rows</th>
                  <th>Validation</th>
                </tr>
              </thead>
              <tbody>
                {result.sheet_summaries.map((sheet) => (
                  <tr key={`${sheet.sheet_name}-${sheet.sheet_type}`}>
                    <td>{sheet.sheet_name}</td>
                    <td>{sheet.sheet_type}</td>
                    <td>
                      <span className="status-badge">{sheet.status}</span>
                    </td>
                    <td>{sheet.row_count ?? 0}</td>
                    <td>{sheet.validation_summary ?? "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="panel-heading-meta">
            <button
              className="secondary-button table-action-button"
              onClick={() =>
                downloadCsv(
                  `upload-preview-${result.workbook_month ?? "workbook"}.csv`,
                  [
                    { key: "reading_date", label: "Date" },
                    { key: "tneb_total", label: "TNEB" },
                    { key: "iex_total", label: "IEX" },
                    { key: "solar_total", label: "Solar" },
                    { key: "tneb_balance", label: "Balance" },
                    { key: "banking_balance", label: "Banking Balance" },
                  ],
                  result.preview_rows,
                )
              }
              type="button"
            >
              Download preview
            </button>
          </div>

          <div className="table-wrap">
            <table className="data-table compact-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>TNEB</th>
                  <th>IEX</th>
                  <th>Solar</th>
                  <th>Balance</th>
                </tr>
              </thead>
              <tbody>
                {result.preview_rows.map((row) => (
                  <tr key={row.reading_date}>
                    <td>{row.reading_date}</td>
                    <td>{row.tneb_total.toFixed(2)}</td>
                    <td>{row.iex_total.toFixed(2)}</td>
                    <td>{row.solar_total.toFixed(2)}</td>
                    <td>{row.tneb_balance.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : null}
    </section>
  );
}
