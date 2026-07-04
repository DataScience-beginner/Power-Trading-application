# Service Architecture

## Platform Shape

The platform is organized as a service-oriented monorepo.

Each service should have:

- its own application code
- its own service metadata file
- its own settings surface
- shared observability conventions
- consistent health endpoints

## Current Service Inventory

1. `client-web`
Client-facing React dashboard and workflow UI.

2. `excel-consumption-service`
Workbook ingestion, normalization, storage, and `Solar Working` calculation.

## Future Service Candidates

- auth and tenant access service
- notifications service
- AI recommendations service
- reporting and export service
- device or meter data integration service
- workflow and approvals service

## Core Architectural Decisions

### Web First

The primary product is web-based. Desktop support can be added later with a thin
wrapper, without changing the backend service boundaries.

### Backend Owns Calculation

`Solar Working` must be generated in service code, not in frontend logic and not
by depending on Excel formulas at runtime.

### Unified Schema With Tenant Isolation

All clients should use a common core schema. Custom behavior should be applied
through configuration, mappings, and rules instead of schema duplication.

### Observable Services

Each service should register metadata such as:

- service key
- owner
- runtime
- ports
- dependencies
- health path
- observability tags

This supports future tracking when the platform grows to many services.
