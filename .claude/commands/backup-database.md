# Database Backup Command

**Created:** 09/17/25 3:27PM ET
**Updated:** 09/24/25 4:40PM - Switched to Docker container method for all backups (more reliable) and added dual backup locations
**Purpose:** Simple, reliable backup and restore procedures for local Supabase database

## Overview

This command provides consistent database backup procedures for the Finances project local Supabase instance. All backups are timestamped and stored in `/backups/` directory.

## When to Use Each Backup Type

### 📊 **Data Backup** (Most Common)
**Use when:** Regular backups of financial data, before major data operations
**Contains:** All transactions, documents, entities - no schema
**Frequency:** Weekly or before major document processing sessions

### 🏗️ **Schema Backup**
**Use when:** Testing migrations, documenting schema changes
**Contains:** Table structures, indexes, constraints - no data
**Frequency:** After schema changes or before migrations

### 💾 **Full Backup** (Complete)
**Use when:** Major system changes, before updates, monthly archives
**Contains:** Everything - schema + data
**Frequency:** Monthly or before major system changes

## Quick Backup Commands

### Create Data Backup (Financial Records Only)
```bash
cd /Users/richkernan/Projects/Finances
TIMESTAMP=$(date +"%Y.%m.%d_%H.%M")
mkdir -p backups
mkdir -p "/Users/richkernan/Desktop/Finance_DB_Backups"
docker exec supabase_db_Finances pg_dump -U postgres --data-only postgres > backups/data-backup-$TIMESTAMP.sql
cp backups/data-backup-$TIMESTAMP.sql "/Users/richkernan/Desktop/Finance_DB_Backups/"
echo "✅ Data backup saved: backups/data-backup-$TIMESTAMP.sql"
echo "✅ Copy saved to: /Users/richkernan/Desktop/Finance_DB_Backups/data-backup-$TIMESTAMP.sql"
ls -lh backups/data-backup-$TIMESTAMP.sql
```

### Create Schema Backup (Structure Only)
```bash
cd /Users/richkernan/Projects/Finances
TIMESTAMP=$(date +"%Y.%m.%d_%H.%M")
mkdir -p backups
mkdir -p "/Users/richkernan/Desktop/Finance_DB_Backups"
docker exec supabase_db_Finances pg_dump -U postgres --schema-only postgres > backups/schema-backup-$TIMESTAMP.sql
cp backups/schema-backup-$TIMESTAMP.sql "/Users/richkernan/Desktop/Finance_DB_Backups/"
echo "✅ Schema backup saved: backups/schema-backup-$TIMESTAMP.sql"
echo "✅ Copy saved to: /Users/richkernan/Desktop/Finance_DB_Backups/schema-backup-$TIMESTAMP.sql"
ls -lh backups/schema-backup-$TIMESTAMP.sql
```

### Create Full Backup (Complete Database)
```bash
cd /Users/richkernan/Projects/Finances
TIMESTAMP=$(date +"%Y.%m.%d_%H.%M")
mkdir -p backups
mkdir -p "/Users/richkernan/Desktop/Finance_DB_Backups"
# Direct container backup - most reliable method
docker exec supabase_db_Finances pg_dump -U postgres postgres > backups/full-backup-$TIMESTAMP.sql
cp backups/full-backup-$TIMESTAMP.sql "/Users/richkernan/Desktop/Finance_DB_Backups/"
echo "✅ Full backup saved: backups/full-backup-$TIMESTAMP.sql"
echo "✅ Copy saved to: /Users/richkernan/Desktop/Finance_DB_Backups/full-backup-$TIMESTAMP.sql"
ls -lh backups/full-backup-$TIMESTAMP.sql
```

### Alternative: Supabase CLI Backup (If Docker Issues)
```bash
cd /Users/richkernan/Projects/Finances
TIMESTAMP=$(date +"%Y.%m.%d_%H.%M")
mkdir -p backups
mkdir -p "/Users/richkernan/Desktop/Finance_DB_Backups"
# Fallback method if Docker container access has issues
supabase db dump --local -f backups/cli-backup-$TIMESTAMP.sql
cp backups/cli-backup-$TIMESTAMP.sql "/Users/richkernan/Desktop/Finance_DB_Backups/"
echo "✅ CLI backup saved: backups/cli-backup-$TIMESTAMP.sql"
echo "✅ Copy saved to: /Users/richkernan/Desktop/Finance_DB_Backups/cli-backup-$TIMESTAMP.sql"
ls -lh backups/cli-backup-$TIMESTAMP.sql
```

## Restore Procedures

### ⚠️ IMPORTANT: Restore Safety
- **Never restore without explicit user confirmation**
- **Always explain what data will be lost/overwritten**
- **Suggest creating a backup before restoring**

### Restore Data Only
```bash
# WARNING: This replaces all current data
cd /Users/richkernan/Projects/Finances
# Truncate all tables first, then restore
docker exec supabase_db_Finances psql -U postgres -d postgres -c "
TRUNCATE transactions, documents, tax_payments, transfers,
asset_notes, real_assets, liabilities, document_accounts,
accounts, institutions, entities RESTART IDENTITY CASCADE;"
docker exec -i supabase_db_Finances psql -U postgres -d postgres < backups/data-backup-YYYYMMDD-HHMMSS.sql
```

### Restore Schema Only
```bash
# WARNING: This rebuilds database structure
cd /Users/richkernan/Projects/Finances
supabase db reset
docker exec -i supabase_db_Finances psql -U postgres -d postgres < backups/schema-backup-YYYYMMDD-HHMMSS.sql
```

### Restore Full Backup
```bash
# WARNING: This replaces everything - most reliable method
cd /Users/richkernan/Projects/Finances
supabase db reset
docker exec -i supabase_db_Finances psql -U postgres -d postgres < backups/full-backup-YYYYMMDD-HHMMSS.sql
```

## File Naming Convention

```
backups/
├── data-backup-2025.09.17_15.27.sql     # Data only
├── schema-backup-2025.09.17_15.27.sql   # Schema only
├── full-backup-2025.09.17_15.28.sql     # Complete backup
└── README.md                            # Backup inventory (optional)

/Users/richkernan/Desktop/Finance_DB_Backups/
├── data-backup-2025.09.17_15.27.sql     # Mirror copy
├── schema-backup-2025.09.17_15.27.sql   # Mirror copy
└── full-backup-2025.09.17_15.28.sql     # Mirror copy
```

## Claude Instructions

### When User Requests "Backup Database"
1. **Ask what type** unless specified:
   - "Data backup (financial records only)"
   - "Schema backup (table structure only)"
   - "Full backup (everything)"
   - "Container backup (most reliable for complex restores)"

2. **Confirm before proceeding:**
   - "Creating [type] backup of local database to backups/[filename]"

3. **Run the appropriate commands above**

4. **Confirm completion:**
   - Show filename and file size
   - Mention what's included
   - Note backup method used

### Recommended Backup Strategy
- **Daily/Weekly:** Data backups for financial records
- **After schema changes:** Schema backups
- **Monthly:** Full backups for complete safety
- **Before major operations:** Container backups (most reliable)

### When User Requests "Restore Database"
1. **⚠️ STOP and warn:**
   - "This will replace/modify existing data"
   - "Recommend creating backup first"

2. **List available backups:**
   ```bash
   ls -la backups/*.sql
   ```

3. **Get explicit confirmation:**
   - Which backup file to use
   - Confirm they understand data will be replaced

4. **Create safety backup before restore:**
   - Always run a full backup first
   - Then proceed with restore

## Verification Commands

### Check Backup File Size
```bash
ls -lh backups/
```

### Verify Backup Contents (peek)
```bash
head -20 backups/[backup-file].sql
tail -10 backups/[backup-file].sql
```

### Check Database Status After Restore
```bash
psql postgresql://postgres:postgres@127.0.0.1:54322/postgres -c "\dt"
psql postgresql://postgres:postgres@127.0.0.1:54322/postgres -c "SELECT COUNT(*) FROM transactions;"
```

## Backup Maintenance

### Clean Old Backups (Manual)
```bash
# Keep last 10 of each type, delete older ones
cd /Users/richkernan/Projects/Finances/backups
ls -t data-backup-*.sql | tail -n +11 | xargs rm -f
ls -t schema-backup-*.sql | tail -n +11 | xargs rm -f
ls -t full-backup-*.sql | tail -n +11 | xargs rm -f
```

### Check Backup Storage Usage
```bash
du -sh backups/
```

## Emergency Recovery

If database is corrupted:
1. Stop Supabase: `supabase stop`
2. Reset database: `supabase db reset`
3. Restore from most recent full backup
4. Verify data integrity with sample queries

---

**Security Note:** Backups contain real financial data. Store securely and never commit to git (already in .gitignore).