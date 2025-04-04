
# ShipVox Technical Requirements Document

## Overview
ShipVox is a shipping middleware application designed to serve as a unified API layer between conversational interfaces (e.g., ElevenLabs agents) and carrier shipping APIs (FedEx, UPS, and eventually USPS). This document defines the technical requirements for implementing the core functionality of the ShipVox engine.

## Functional Scope

### 1. Input Reception (Upstream API → ShipVox)
- Accept POST request from upstream system (e.g., voice agent)
- Required fields:
    - `originZip` (string)
    - `destinationZip` (string)
    - `weight` (float, in pounds)
    - `dimensions` (object with `length`, `width`, `height` in inches)
- Optional fields:
    - `pickupRequested` (boolean)

### 2. Data Normalization & Transformation
- Normalize input units (ensure imperial)
- Validate fields (ZIP format, positive weight/dimensions)
- Prepare carrier-agnostic "RateRequest" object:
    - Normalized ZIPs
    - Weight and dimensions
    - Optional metadata (e.g., pickup instructions)

### 3. Rate Request Logic
- Send normalized RateRequest to:
    - FedEx API using FedExRates module
    - UPS API via equivalent UPSRates module (WIP or pending)
- Handle OAuth token management via carrier-specific auth managers (e.g., FedExAuth)

### 4. Rate Response Handling
- Collect rate quotes from each carrier
- Extract relevant details from each (cost, estimated delivery time, service level)
- Apply apples-to-apples comparison algorithm:
    - Normalize service types across carriers
    - Determine:
        - Cheapest available rate
        - Fastest (and reasonably priced) option
- Format outbound response with:
    - `cheapestOption`
    - `cheapestFastestOption`
    - Source carrier, service name, cost, ETA

### 5. Outbound Quote Response (ShipVox → Upstream API)
- Send JSON response with top 2 rate options to upstream
- Response must be synchronous and complete within timeout (TBD)

### 6. Label Creation Flow
- Receive POST request from upstream API to generate a label
- Payload includes:
    - Selected carrier (FedEx or UPS)
    - Selected service
    - Additional required shipping details (collected conversationally by voice interface)
- Validate payload and enrich with:
    - Ship-from/ship-to contact info
    - Address details
    - Service type
    - Packaging type (if applicable)
- Send request to carrier Ship API
- Return label PDF, QR code, and tracking number in response

### 7. Pickup Scheduling (Optional)
- If `pickupRequested == true`, send POST to carrier Pickup API with:
    - Pickup location
    - Earliest/latest pickup times (defaults available)
    - Contact details
- Log pickup confirmation response

## Non-Functional Requirements
- **Security**: Use OAuth2 for carrier access. Sanitize and validate all inbound data.
- **Scalability**: System must support future carrier integrations (USPS, DHL).
- **Error Handling**: Graceful failure with descriptive errors. Retry logic for rate and label requests.
- **Latency**: Total roundtrip time for rate request should be < 3 seconds.
- **Extensibility**: Modular rate engines per carrier.

## Existing Functionality (To Be Audited or Refactored)
- ✅ FedEx OAuth authentication (via `FedExAuth`)
- ✅ FedEx rate quoting (via `FedExRates`)
- ✅ Frontend rate input form (React/TypeScript)
- ✅ Display of FedEx shipping options
- ❌ UPS integration (planned next)
- ❌ Unified rate comparison logic
- ❌ Label generation + pickup scheduling

## Future Enhancements
- USPS rate engine
- Address validation via carrier APIs
- Saved shipment history per user
- Payment integration for real-time cost capture
