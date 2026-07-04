import { useMemo, useState } from "react";
import { downloadCsv } from "../lib/export";
import type { WorkbookResultsResponse } from "../lib/types";

type SolarWorkingResultsPanelProps = {
  result: WorkbookResultsResponse | null;
  isLoading: boolean;
  error: string;
};


// The result table is intentionally compact now so the calculation output is easy to validate.
export function SolarWorkingResultsPanel({
  result,
  isLoading,
  error,
}: SolarWorkingResultsPanelProps) {
  const [balanceFilter, setBalanceFilter] = useState<
    "all" | "positive" | "negative"
  >("all");
  const finalBalance =
    result && result.rows.length > 0
      ? result.rows[result.rows.length - 1].tneb_balance
      : 0;
  const filteredRows = useMemo(() => {
    if (!result) {
      return [];
    }
    if (balanceFilter === "positive") {
      return result.rows.filter((row) => row.tneb_balance >= 0);
    }
    if (balanceFilter === "negative") {
      return result.rows.filter((row) => row.tneb_balance < 0);
    }
    return result.rows;
  }, [balanceFilter, result]);

  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Solar Working Results</p>
          <h3>Daily Output Table</h3>
        </div>
        <div className="panel-heading-meta">
          <span className="status-badge">
            {result?.workbook_month ?? "No month"}
          </span>
          <span className="status-badge status-badge-accent">
            Final balance {finalBalance.toFixed(2)}
          </span>
          <button
            className="secondary-button table-action-button"
            disabled={!result}
            onClick={() => {
              if (!result) {
                return;
              }
              downloadCsv(
                `solar-working-${result.workbook_month ?? "results"}.csv`,
                [
                  { key: "reading_date", label: "Date" },
                  { key: "tneb_total", label: "TNEB" },
                  { key: "iex_total", label: "IEX" },
                  { key: "solar_total", label: "Solar" },
                  { key: "tneb_balance", label: "Balance" },
                  { key: "banking_balance", label: "Banking Balance" },
                ],
                filteredRows,
              );
            }}
            type="button"
          >
            Export CSV
          </button>
        </div>
      </div>
      <div className="filter-chip-row">
        <button
          className={`filter-chip${balanceFilter === "all" ? " is-active" : ""}`}
          onClick={() => setBalanceFilter("all")}
          type="button"
        >
          All rows
        </button>
        <button
          className={`filter-chip${balanceFilter === "positive" ? " is-active" : ""}`}
          onClick={() => setBalanceFilter("positive")}
          type="button"
        >
          Positive balance
        </button>
        <button
          className={`filter-chip${balanceFilter === "negative" ? " is-active" : ""}`}
          onClick={() => setBalanceFilter("negative")}
          type="button"
        >
          Negative balance
        </button>
      </div>
      {error ? <p className="error-text">{error}</p> : null}
      {isLoading ? <p className="muted">Loading calculated rows...</p> : null}
      {!isLoading && !result ? (
        <p className="muted">Select a workbook to view calculated output.</p>
      ) : null}
      {result ? (
        <div className="table-wrap">
          <table className="data-table">
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
              {filteredRows.map((row) => (
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
      ) : null}
    </section>
  );
}
