## ADDED Requirements

### Requirement: Tenant Session Isolation
The `SessionPool` class SHALL manage independent browser instances mapped by a unique `tenant_id` to ensure separate, isolated browser sessions for different operations or tenants.

#### Scenario: Isolated Tenant Creation
- **WHEN** a session is requested for tenant "A" and tenant "B"
- **THEN** the system SHALL create two distinct browser instances running with separate configurations.

### Requirement: Resource Leaks Prevention
The `SessionPool` class MUST support clean, robust closing mechanisms (`close` and `close_all`) that kill the underlying browser processes and release file locks on the profile directory.

#### Scenario: Closing All Active Browser Instances
- **WHEN** `close_all` is called on the `SessionPool`
- **THEN** it SHALL call `kill()` on all managed browser sessions and clear the internal registry completely.
