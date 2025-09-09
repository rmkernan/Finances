# ADR 001: Supabase PostgreSQL over SQLite

**Created:** 09/09/25 4:52PM ET  
**Updated:** 09/09/25 4:52PM ET  
**Status:** Accepted  
**Deciders:** Project architect, based on analysis in [context.md](/Users/richkernan/Projects/Finances/docs/archive/context.md)

## Context

The financial data management system requires a database solution that can handle:
- Precise financial calculations without floating-point errors
- Complex JSON document storage for PDF extraction results
- Multi-user access from different devices (PC, Mac, remote)
- Real-time updates for dashboard functionality
- Robust backup and recovery capabilities
- ACID compliance for financial data integrity

## Decision

We will use **Supabase (PostgreSQL) via Docker** hosted on Mac Mini M4, rather than SQLite or other alternatives.

## Rationale

### PostgreSQL Advantages for Financial Data

#### Precision Mathematics
- **NUMERIC/DECIMAL types** - Exact decimal arithmetic, no floating-point errors
- **Critical for financial data** - $58,535.44 remains exactly $58,535.44, not $58,535.439999997
- **SQLite limitation** - Uses floating-point for all numeric operations, unsuitable for currency

#### Advanced Data Types
- **JSON/JSONB support** - Store complex PDF extraction results efficiently
- **Date/time precision** - Proper handling of tax periods, settlement dates
- **Array support** - Store multiple tax categories per transaction
- **Custom types** - Can define financial-specific data types

#### ACID Compliance & Concurrency
- **Full ACID transactions** - Critical for financial data consistency
- **Multi-user access** - Handle simultaneous access from PC and laptop
- **Row-level locking** - Prevent data corruption during concurrent operations
- **SQLite limitation** - Database-level locking, poor concurrent write performance

### Supabase Specific Benefits

#### Real-Time Features
- **Live dashboard updates** - See new transactions as documents are processed
- **WebSocket subscriptions** - Instant notification of reconciliation discrepancies
- **Collaborative features** - Multiple users can monitor processing status

#### Development Productivity
- **Auto-generated REST API** - Instant API for all database operations
- **Built-in authentication** - User management for remote access
- **Admin dashboard** - Database inspection and management tools
- **Type generation** - Auto-generated TypeScript types for frontend

#### Infrastructure Simplicity
- **Docker deployment** - Single-command setup on Mac Mini
- **Integrated backup** - Built-in Point-in-Time Recovery (PITR)
- **Monitoring tools** - Performance metrics and query analysis
- **Extension ecosystem** - Access to PostgreSQL extensions as needed

### Mac Mini M4 Host Platform

#### Always-On Reliability
- **Silent operation** - No fans under normal financial workload
- **Low power consumption** - 10W idle, suitable for 24/7 operation
- **Apple Silicon efficiency** - M4 handles database operations efficiently
- **Better than Windows** - No sleep/wake issues affecting database availability

#### Network Accessibility
- **Local network access** - `http://mac-mini.local:3000` from any device
- **Tailscale VPN** - Secure remote access when traveling
- **SMB file sharing** - Easy document upload from PC

## Alternatives Considered

### SQLite
**Pros:**
- Simple deployment, single file
- No network configuration needed
- Lightweight resource usage

**Cons:**
- **Floating-point math** - Unsuitable for financial precision
- **Limited concurrency** - Database-level locking
- **No real-time features** - Would require custom implementation
- **Poor remote access** - File-based, difficult to access remotely

**Decision:** Rejected due to precision and concurrency limitations

### Cloud PostgreSQL (AWS RDS, Google Cloud SQL)
**Pros:**
- Managed service, automatic backups
- High availability and scaling
- Professional database administration

**Cons:**
- **Monthly costs** - $50-100+ per month for suitable performance
- **Data privacy concerns** - Financial data stored with cloud provider
- **Network dependency** - Requires internet for all operations
- **Latency** - Slower than local database for document processing

**Decision:** Rejected due to cost and privacy considerations

### Self-Hosted PostgreSQL (Docker)
**Pros:**
- Full control over configuration
- Lower cost than cloud solutions
- Standard PostgreSQL features

**Cons:**
- **More complex setup** - Manual configuration of all features
- **No built-in API** - Would need custom REST API development
- **Manual backup management** - Custom backup and recovery procedures
- **No real-time features** - Would require WebSocket implementation

**Decision:** Supabase provides all PostgreSQL benefits plus additional features

## Implementation Details

### Docker Setup
```yaml
# docker-compose.yml
version: '3.8'
services:
  supabase:
    image: supabase/postgres
    environment:
      POSTGRES_PASSWORD: [secure_password]
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
```

### Access Configuration
- **Local network:** `postgresql://localhost:5432/postgres`
- **Supabase API:** `http://mac-mini.local:3000`
- **Remote access:** Via Tailscale VPN tunnel

### Backup Strategy
- **Supabase PITR:** Continuous backup with point-in-time recovery
- **Mac Time Machine:** Host-level backup of Docker volumes
- **Export scripts:** Periodic full database exports to `/data/exports/`

## Success Metrics

### Performance Targets
- **Document processing:** Handle 20-page PDF extraction within 30 seconds
- **Dashboard load time:** Initial page load under 2 seconds
- **Concurrent access:** Support PC + laptop simultaneous access
- **Query response:** Financial summaries under 1 second

### Reliability Targets
- **Uptime:** 99.9% availability (< 9 hours downtime per year)
- **Data integrity:** Zero financial calculation errors
- **Backup recovery:** Full recovery capability within 1 hour
- **Remote access:** Reliable operation over Tailscale VPN

## Consequences

### Positive
- **Precise financial calculations** - No floating-point rounding errors
- **Real-time collaboration** - Multiple users can work simultaneously
- **Professional database features** - ACID compliance, proper indexing
- **Rapid development** - Auto-generated APIs and admin tools
- **Future-proof** - Can handle additional complexity as system grows

### Negative
- **Resource usage** - Higher memory/CPU usage than SQLite
- **Network dependency** - Requires network for remote access
- **Complexity** - More moving parts than file-based database
- **Mac Mini dependency** - Single point of failure (mitigated by backups)

## Related Decisions

- **ADR 002:** [Host platform selection - Mac Mini M4] (pending)
- **ADR 003:** [PDF processing strategy - Claude AI] (pending)
- **ADR 004:** [Remote access method - Tailscale VPN] (pending)

## References

- [PostgreSQL NUMERIC documentation](https://www.postgresql.org/docs/current/datatype-numeric.html)
- [Supabase Docker setup guide](https://supabase.com/docs/guides/self-hosting/docker)
- [Financial precision requirements analysis](/Users/richkernan/Projects/Finances/docs/archive/context.md#technology-stack-decisions--rationale)
- [Original schema design](/Users/richkernan/Projects/Finances/docs/archive/schema.md)

---

*This decision prioritizes data accuracy and system reliability over simplicity, reflecting the critical nature of financial data management.*