import type {
  AdminOverviewResponse,
  AuthenticatedUser,
  LoginPayload,
  LoginResult,
  PortalSummary,
  WorkbookListItem,
  WorkbookResultsResponse,
  WorkbookUploadResponse,
} from "./types";

function resolveApiBaseUrl(): string {
  const configuredUrl = import.meta.env.VITE_API_BASE_URL?.trim();
  if (configuredUrl) {
    return configuredUrl;
  }

  if (typeof window !== "undefined") {
    return `${window.location.protocol}//${window.location.hostname}:8000`;
  }

  return "http://localhost:8000";
}

const apiBaseUrl = resolveApiBaseUrl();


async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    ...init,
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => null);
    throw new Error(errorBody?.detail ?? "Request failed.");
  }

  return (await response.json()) as T;
}


export function login(payload: LoginPayload): Promise<LoginResult> {
  return request<LoginResult>("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}


export function fetchCurrentUser(token: string): Promise<AuthenticatedUser> {
  return request<AuthenticatedUser>("/api/v1/auth/me", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}


export function fetchAdminSummary(token: string): Promise<PortalSummary> {
  return request<PortalSummary>("/api/v1/auth/admin/summary", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}


export function fetchClientSummary(token: string): Promise<PortalSummary> {
  return request<PortalSummary>("/api/v1/auth/client/summary", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export function fetchAdminOverview(token: string): Promise<AdminOverviewResponse> {
  return request<AdminOverviewResponse>("/api/v1/auth/admin/overview", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export function fetchWorkbookHistory(token: string): Promise<WorkbookListItem[]> {
  return request<WorkbookListItem[]>("/api/v1/workbooks", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export function fetchWorkbookResults(
  token: string,
  workbookId: string,
): Promise<WorkbookResultsResponse> {
  return request<WorkbookResultsResponse>(
    `/api/v1/workbooks/${workbookId}/solar-working`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  );
}


export async function uploadWorkbook(
  token: string,
  file: File,
): Promise<WorkbookUploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${apiBaseUrl}/api/v1/workbooks/upload`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => null);
    throw new Error(errorBody?.detail ?? "Upload failed.");
  }

  return (await response.json()) as WorkbookUploadResponse;
}
