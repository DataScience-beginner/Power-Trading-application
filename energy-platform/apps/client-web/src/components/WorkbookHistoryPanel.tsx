import { useMemo, useState } from "react";
import { downloadCsv } from "../lib/export";
import type { WorkbookListItem } from "../lib/types";

type WorkbookHistoryPanelProps = {
  items: WorkbookListItem[];
  selectedWorkbookId: string | null;
  onSelect: (workbookId: string) => void;
};


// Keeping the history table isolated makes it easier to add filters and paging later.
export function WorkbookHistoryPanel({
  items,
  selectedWorkbookId,
  onSelect,
}: WorkbookHistoryPanelProps) {
  const [statusFilter, setStatusFilter] = useState<"all" | "calculated">("all");

  const filteredItems = useMemo(() => {
    if (statusFilter === "all") {
      return items;
    }
    return items.filter((item) => item.status === statusFilter);
  }, [items, statusFilter]);

  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Workbook History</p>
          <h3>Available Calculation Batches</h3>
        </div>
        <div className="panel-heading-meta">
          <span className="status-badge">{filteredItems.length} files</span>
          <button
            className="secondary-button table-action-button"
            onClick={() =>
              downloadCsv(
                "workbook-history.csv",
                [
                  { key: "workbook_month", label: "Month" },
                  { key: "file_name", label: "File" },
                  { key: "status", label: "Status" },
                  { key: "solar_working_rows", label: "Rows" },
                  { key: "uploaded_at", label: "Uploaded At" },
                ],
                filteredItems,
              )
            }
            type="button"
          >
            Export CSV
          </button>
        </div>
      </div>
      <div className="filter-chip-row">
        <button
          className={`filter-chip${statusFilter === "all" ? " is-active" : ""}`}
          onClick={() => setStatusFilter("all")}
          type="button"
        >
          All files
        </button>
        <button
          className={`filter-chip${statusFilter === "calculated" ? " is-active" : ""}`}
          onClick={() => setStatusFilter("calculated")}
          type="button"
        >
          Calculated only
        </button>
      </div>
      {filteredItems.length === 0 ? (
        <p className="muted">No workbooks uploaded yet.</p>
      ) : (
        <div className="table-wrap">
          <table className="data-table compact-table">
            <thead>
              <tr>
                <th>Month</th>
                <th>File</th>
                <th>Status</th>
                <th>Rows</th>
              </tr>
            </thead>
            <tbody>
              {filteredItems.map((item) => (
                <tr
                  className={
                    item.workbook_id === selectedWorkbookId ? "selected-row" : ""
                  }
                  key={item.workbook_id}
                  onClick={() => onSelect(item.workbook_id)}
                >
                  <td>{item.workbook_month ?? "unknown"}</td>
                  <td>{item.file_name}</td>
                  <td>
                    <span className="status-badge">{item.status}</span>
                  </td>
                  <td>{item.solar_working_rows}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
