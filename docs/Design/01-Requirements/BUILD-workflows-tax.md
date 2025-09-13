# BUILD: Tax Analysis Workflows Implementation Guide

**Created:** 09/12/25 5:59PM ET  
**Purpose:** Complete context for tax analysis, reporting, and payment tracking workflows with Georgia exemptions  
**Status:** Ready for implementation

## LLM Context Summary
**Task:** Implement tax analysis workflows with Georgia municipal exemptions, multi-entity consolidation, and payment tracking  
**Prerequisites:** Tax calculation engine, Georgia exemption rules (FSIXX ~97%, SPAXX ~55%), multi-entity data aggregation  
**Key Decisions Made:** Automated exemption calculations, quarterly payment tracking, consolidated reporting, S-Corp pass-through handling  
**Output Expected:** Tax analysis dashboards, payment tracking system, export functionality for tax software

## Quick Reference

**Core Workflows:**
- **Workflow 4:** Tax Analysis & Reporting (income categorization, exemption calculations)
- **Workflow 5:** Tax Payment Tracking (quarterly estimates, payment history)
- **Workflow 6:** Year-Over-Year Comparisons (comparative analysis, trend reporting)

**Key Components:** TaxSummary, PaymentTracker, ExemptionCalculator, EntityTaxBreakdown, YoYComparison

**Tax Rules:** FSIXX ~97% GA exempt, SPAXX ~55% GA exempt, GA munis double exempt, other state munis GA taxable

## Navigation Architecture (For Context)

### Context Hierarchy for Tax Views
```
Global Tax Center (All Entities)
    ↓
Entity Tax Summary (Single Entity)
    ↓
Account Tax Detail (Account-Specific)
    ↓
Transaction Tax Classification (Individual Transactions)
```

### Tax Data Flow
```
Transaction → Tax Classification → Entity Aggregation → Consolidated Reporting
    ↓              ↓                    ↓                      ↓
Raw Data    Apply Exemptions     Entity Totals        Combined Tax Liability
```

---

## Workflow 4: Tax Analysis & Reporting

**User Story:** "I need to prepare quarterly taxes for each entity and understand total liability"

### Core Components

#### 1. Tax Center Dashboard
```typescript
interface TaxCenterData {
  currentYear: number
  selectedPeriod: 'Q1' | 'Q2' | 'Q3' | 'Q4' | 'YTD'
  entities: EntityTaxSummary[]
  consolidated: ConsolidatedTaxSummary
  exemptions: ExemptionSummary
  payments: PaymentSummary
}

interface EntityTaxSummary {
  entityId: string
  entityName: string
  entityType: 'S-Corp' | 'LLC' | 'Partnership' | 'Individual'
  taxableIncome: {
    federal: number
    state: number
  }
  incomeBreakdown: {
    ordinaryDividends: TaxableAmount
    qualifiedDividends: TaxableAmount
    interest: TaxableAmount
    capitalGains: TaxableAmount
    municipalBonds: TaxableAmount
  }
  estimatedTax: {
    federal: number
    state: number
    selfEmployment?: number
  }
  paymentsDue: PaymentDue[]
}

interface TaxableAmount {
  gross: number
  federalTaxable: number
  stateTaxable: number
  exemptAmount: number
  exemptionType?: string
}
```

#### 2. Entity-Specific Tax Summary Component
**Layout for Single Entity:**
```
┌──────────────────────────────────────────────────────────────┐
│ Milton Preschool Inc - Q1 2024 Tax Summary                   │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ Income Summary:                                              │
│ ┌─────────────────────┬──────────┬──────────┬──────────────┐ │
│ │ Income Type         │ Amount   │ Federal  │ Georgia      │ │
│ ├─────────────────────┼──────────┼──────────┼──────────────┤ │
│ │ FSIXX Dividends     │ $4,327   │ $4,327   │ $130 (3%)    │ │
│ │ SPAXX Dividends     │ $2       │ $2       │ $1 (45%)     │ │
│ │ Corporate Dividends │ $12,000  │ $12,000  │ $12,000      │ │
│ │ Municipal (GA)      │ $5,000   │ $0       │ $0           │ │
│ │ Municipal (Other)   │ $3,000   │ $0       │ $3,000       │ │
│ │ Capital Gains       │ $25,000  │ $25,000  │ $25,000      │ │
│ ├─────────────────────┼──────────┼──────────┼──────────────┤ │
│ │ TOTAL               │ $49,329  │ $41,329  │ $40,131      │ │
│ └─────────────────────┴──────────┴──────────┴──────────────┘ │
│                                                              │
│ Estimated Tax Due:                                           │
│ Federal: $8,265 | Georgia: $2,407                            │
│                                                              │
│ [Export for Tax Software] [Generate 1120S Draft]             │
└──────────────────────────────────────────────────────────────┘
```

#### 3. Tax Calculation Engine
```typescript
interface TaxCalculationRules {
  year: number
  federalRates: TaxBracket[]
  stateRates: TaxBracket[]
  exemptions: ExemptionRule[]
  standardDeductions: {
    individual: number
    marriedJoint: number
    marriedSeparate: number
    headOfHousehold: number
  }
}

interface ExemptionRule {
  security: string // 'FSIXX', 'SPAXX', etc.
  federalExempt: boolean
  stateExempt: boolean
  partialExemption?: {
    state: number // percentage (e.g., 0.97 for 97%)
    reason: string
  }
}

class TaxCalculator {
  private rules: TaxCalculationRules
  
  calculateEntityTax(entityId: string, period: TaxPeriod): EntityTaxSummary {
    const transactions = this.getEntityTransactions(entityId, period)
    const incomeBreakdown = this.categorizeIncome(transactions)
    const exemptionsApplied = this.applyExemptions(incomeBreakdown)
    const taxableAmounts = this.calculateTaxableAmounts(exemptionsApplied)
    const estimatedTax = this.calculateTax(taxableAmounts)
    
    return {
      entityId,
      entityName: this.getEntityName(entityId),
      entityType: this.getEntityType(entityId),
      taxableIncome: taxableAmounts,
      incomeBreakdown: exemptionsApplied,
      estimatedTax
    }
  }
  
  applyExemptions(income: IncomeBreakdown): IncomeBreakdown {
    const exempted = { ...income }
    
    // FSIXX exemption - ~97% Georgia exempt
    if (exempted.fsixxDividends > 0) {
      exempted.fsixxDividends = {
        gross: exempted.fsixxDividends.gross,
        federalTaxable: exempted.fsixxDividends.gross, // Fully federal taxable
        stateTaxable: exempted.fsixxDividends.gross * 0.03, // ~3% Georgia taxable
        exemptAmount: exempted.fsixxDividends.gross * 0.97,
        exemptionType: 'Georgia Treasury Fund Exemption'
      }
    }
    
    // SPAXX exemption - ~55% Georgia exempt  
    if (exempted.spaxxDividends > 0) {
      exempted.spaxxDividends = {
        gross: exempted.spaxxDividends.gross,
        federalTaxable: exempted.spaxxDividends.gross, // Fully federal taxable
        stateTaxable: exempted.spaxxDividends.gross * 0.45, // ~45% Georgia taxable
        exemptAmount: exempted.spaxxDividends.gross * 0.55,
        exemptionType: 'Money Market Fund Partial Exemption'
      }
    }
    
    // Georgia municipal bonds - double exempt
    if (exempted.gaMunicipalBonds > 0) {
      exempted.gaMunicipalBonds = {
        gross: exempted.gaMunicipalBonds.gross,
        federalTaxable: 0, // Federal exempt
        stateTaxable: 0,   // Georgia exempt
        exemptAmount: exempted.gaMunicipalBonds.gross,
        exemptionType: 'Georgia Municipal Bond Double Exemption'
      }
    }
    
    // Other state municipal bonds - federal exempt, Georgia taxable
    if (exempted.otherStateMunicipalBonds > 0) {
      exempted.otherStateMunicipalBonds = {
        gross: exempted.otherStateMunicipalBonds.gross,
        federalTaxable: 0, // Federal exempt
        stateTaxable: exempted.otherStateMunicipalBonds.gross, // Georgia taxable
        exemptAmount: 0,
        exemptionType: 'Federal Exempt Only'
      }
    }
    
    return exempted
  }
}
```

#### 4. Data Source Queries
```sql
-- Tax summary by entity and period
WITH income_classification AS (
  SELECT 
    a.entity_id,
    e.name as entity_name,
    e.entity_type,
    
    -- FSIXX dividends
    SUM(CASE WHEN t.symbol = 'FSIXX' AND t.transaction_type = 'dividend' 
             THEN t.amount ELSE 0 END) as fsixx_dividends,
             
    -- SPAXX dividends  
    SUM(CASE WHEN t.symbol = 'SPAXX' AND t.transaction_type = 'dividend'
             THEN t.amount ELSE 0 END) as spaxx_dividends,
             
    -- Corporate dividends (non-fund)
    SUM(CASE WHEN t.transaction_type = 'dividend' 
             AND t.symbol NOT IN ('FSIXX', 'SPAXX')
             AND s.security_type = 'stock'
             THEN t.amount ELSE 0 END) as corporate_dividends,
             
    -- Municipal bond interest
    SUM(CASE WHEN t.transaction_type = 'interest'
             AND s.security_type = 'municipal_bond'
             AND s.issuer_state = 'GA'
             THEN t.amount ELSE 0 END) as ga_municipal_interest,
             
    SUM(CASE WHEN t.transaction_type = 'interest'
             AND s.security_type = 'municipal_bond' 
             AND s.issuer_state != 'GA'
             THEN t.amount ELSE 0 END) as other_state_municipal_interest,
             
    -- Capital gains
    SUM(CASE WHEN t.transaction_type IN ('sell', 'capital_gain')
             AND t.holding_period > 365
             THEN t.realized_gain ELSE 0 END) as long_term_capital_gains,
             
    SUM(CASE WHEN t.transaction_type IN ('sell', 'capital_gain')
             AND t.holding_period <= 365
             THEN t.realized_gain ELSE 0 END) as short_term_capital_gains,
             
    -- Regular interest (non-municipal)
    SUM(CASE WHEN t.transaction_type = 'interest'
             AND s.security_type NOT IN ('municipal_bond')
             THEN t.amount ELSE 0 END) as taxable_interest
             
  FROM transactions t
  JOIN accounts a ON t.account_id = a.id
  JOIN entities e ON a.entity_id = e.id
  LEFT JOIN securities s ON t.security_id = s.id
  WHERE t.date >= $period_start 
    AND t.date <= $period_end
    AND ($entity_id IS NULL OR a.entity_id = $entity_id)
  GROUP BY a.entity_id, e.name, e.entity_type
),
tax_calculations AS (
  SELECT *,
    -- Apply Georgia exemptions
    fsixx_dividends as fsixx_federal_taxable,
    fsixx_dividends * 0.03 as fsixx_georgia_taxable,
    
    spaxx_dividends as spaxx_federal_taxable,  
    spaxx_dividends * 0.45 as spaxx_georgia_taxable,
    
    -- Municipal bonds
    0 as ga_municipal_federal_taxable,
    0 as ga_municipal_georgia_taxable,
    
    0 as other_municipal_federal_taxable,
    other_state_municipal_interest as other_municipal_georgia_taxable,
    
    -- Regular income (fully taxable)
    corporate_dividends as corporate_dividends_federal_taxable,
    corporate_dividends as corporate_dividends_georgia_taxable,
    
    long_term_capital_gains as ltcg_federal_taxable,
    long_term_capital_gains as ltcg_georgia_taxable,
    
    short_term_capital_gains as stcg_federal_taxable, 
    short_term_capital_gains as stcg_georgia_taxable,
    
    taxable_interest as interest_federal_taxable,
    taxable_interest as interest_georgia_taxable
    
  FROM income_classification
),
entity_totals AS (
  SELECT *,
    -- Federal totals
    fsixx_federal_taxable + spaxx_federal_taxable + 
    ga_municipal_federal_taxable + other_municipal_federal_taxable +
    corporate_dividends_federal_taxable + ltcg_federal_taxable + 
    stcg_federal_taxable + interest_federal_taxable as total_federal_taxable,
    
    -- Georgia totals  
    fsixx_georgia_taxable + spaxx_georgia_taxable +
    ga_municipal_georgia_taxable + other_municipal_georgia_taxable +
    corporate_dividends_georgia_taxable + ltcg_georgia_taxable +
    stcg_georgia_taxable + interest_georgia_taxable as total_georgia_taxable
    
  FROM tax_calculations
)
SELECT * FROM entity_totals
ORDER BY entity_name;
```

### Key Features

#### 1. Exemption Calculation Accuracy
```typescript
interface ExemptionValidator {
  validateFSIXXExemption(amount: number, year: number): ExemptionResult {
    // Validate ~97% Georgia exemption for FSIXX
    const exemptionRate = this.getFSIXXExemptionRate(year) // Should be ~0.97
    const georgiaExempt = amount * exemptionRate
    const georgiaTaxable = amount - georgiaExempt
    
    return {
      gross: amount,
      federalTaxable: amount, // Always fully federal taxable
      stateTaxable: georgiaTaxable,
      exemptAmount: georgiaExempt,
      exemptionRate,
      validated: true,
      notes: `Georgia Treasury fund exemption: ${(exemptionRate * 100).toFixed(1)}%`
    }
  }
  
  validateSPAXXExemption(amount: number, year: number): ExemptionResult {
    // Validate ~55% Georgia exemption for SPAXX
    const exemptionRate = this.getSPAXXExemptionRate(year) // Should be ~0.55
    const georgiaExempt = amount * exemptionRate  
    const georgiaTaxable = amount - georgiaExempt
    
    return {
      gross: amount,
      federalTaxable: amount, // Always fully federal taxable
      stateTaxable: georgiaTaxable,
      exemptAmount: georgiaExempt,
      exemptionRate,
      validated: true,
      notes: `Money market fund partial exemption: ${(exemptionRate * 100).toFixed(1)}%`
    }
  }
}
```

#### 2. Multi-Entity Consolidation
**Consolidated Multi-Entity Tax View:**
```
┌─────────────────────────────────────────────────────────────-┐
│ All Entities - Q1 2024 Tax Summary                           │
├─────────────────────────────────────────────────────────────-┤
│                                                              │
│ Total Tax Liability (Flows to Personal):                     │
│ Federal: $45,678 | Georgia: $8,234                           │
│                                                              │
│ By Entity:                                                   │
│ ┌─────────────────────┬──────────┬──────────┬──────────────┐ │
│ │ Entity              │ Income   │ Fed Tax  │ GA Tax       │ │
│ ├─────────────────────┼──────────┼──────────┼──────────────┤ │
│ │ Milton Preschool    │ $49,329  │ $8,265   │ $2,407       │ │
│ │ Entity A Corp       │ $75,000  │ $15,000  │ $4,500       │ │
│ │ Entity B LLC*       │ $35,000  │ $7,000   │ $2,100       │ │
│ │ Entity C Corp       │ $45,000  │ $9,000   │ $2,700       │ │
│ │ Personal           │ $32,500  │ $6,413   │ -$3,473**     │ │
│ ├─────────────────────┼──────────┼──────────┼──────────────┤ │
│ │ TOTAL               │ $236,829 │ $45,678  │ $8,234       │ │
│ └─────────────────────┴──────────┴──────────┴──────────────┘ │
│ * Pass-through entity  ** After credits                      │
│                                                              │
│ [Generate Consolidated Report] [Export All]                  │
└──────────────────────────────────────────────────────────────┘
```

#### 3. Income Type Analysis Component
```typescript
function IncomeTypeAnalysis({ entities, period }: { entities: string[], period: TaxPeriod }) {
  const { data } = useIncomeAnalysis(entities, period)
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>{period} - Income Analysis by Type (All Entities)</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Income Category</TableHead>
              <TableHead className="text-right">Amount</TableHead>
              <TableHead className="text-right">Federal</TableHead>
              <TableHead className="text-right">Georgia</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow>
              <TableCell className="font-medium">Ordinary Dividends</TableCell>
              <TableCell className="text-right">{formatCurrency(data.ordinaryDividends.gross)}</TableCell>
              <TableCell className="text-right">{formatCurrency(data.ordinaryDividends.federalTaxable)}</TableCell>
              <TableCell className="text-right">{formatCurrency(data.ordinaryDividends.stateTaxable)}</TableCell>
            </TableRow>
            <TableRow className="pl-4 text-sm text-muted-foreground">
              <TableCell className="pl-8">FSIXX (97% exempt)</TableCell>
              <TableCell className="text-right">{formatCurrency(data.fsixxDividends.gross)}</TableCell>
              <TableCell className="text-right">{formatCurrency(data.fsixxDividends.federalTaxable)}</TableCell>
              <TableCell className="text-right">{formatCurrency(data.fsixxDividends.stateTaxable)}</TableCell>
            </TableRow>
            <TableRow className="pl-4 text-sm text-muted-foreground">
              <TableCell className="pl-8">SPAXX (55% exempt)</TableCell>
              <TableCell className="text-right">{formatCurrency(data.spaxxDividends.gross)}</TableCell>
              <TableCell className="text-right">{formatCurrency(data.spaxxDividends.federalTaxable)}</TableCell>
              <TableCell className="text-right">{formatCurrency(data.spaxxDividends.stateTaxable)}</TableCell>
            </TableRow>
            <TableRow className="pl-4 text-sm text-muted-foreground">
              <TableCell className="pl-8">Corporate</TableCell>
              <TableCell className="text-right">{formatCurrency(data.corporateDividends.gross)}</TableCell>
              <TableCell className="text-right">{formatCurrency(data.corporateDividends.federalTaxable)}</TableCell>
              <TableCell className="text-right">{formatCurrency(data.corporateDividends.stateTaxable)}</TableCell>
            </TableRow>
            {/* Additional rows for other income types... */}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}
```

### Acceptance Criteria

- [ ] **GIVEN** user selects a tax year and quarter, **WHEN** data exists, **THEN** display income breakdown by tax category
- [ ] **GIVEN** income is displayed, **THEN** show federal taxable vs state taxable amounts
- [ ] **GIVEN** FSIXX dividends exist, **THEN** apply 97% Georgia exemption automatically
- [ ] **GIVEN** SPAXX dividends exist, **THEN** apply 55% Georgia exemption automatically  
- [ ] **GIVEN** multiple entities selected, **THEN** show consolidated view with per-entity breakdown
- [ ] **GIVEN** user requests export, **THEN** generate CSV with all tax-relevant transactions

### Business Rules

#### Tax Year Definition
- Tax year = calendar year (Jan 1 - Dec 31)
- Quarterly periods: Q1 (Jan-Mar), Q2 (Apr-Jun), Q3 (Jul-Sep), Q4 (Oct-Dec)
- YTD calculations include all quarters through selected quarter

#### Georgia Exemption Rules
- **FSIXX (Federal Short Investment Grade Fund):** ~97% Georgia state tax exempt, 100% federal taxable
- **SPAXX (Fidelity Government Money Market):** ~55% Georgia state tax exempt, 100% federal taxable
- **Georgia Municipal Bonds:** 100% federal exempt, 100% Georgia exempt (double exempt)
- **Other State Municipal Bonds:** 100% federal exempt, 100% Georgia taxable

#### Entity Tax Treatment
- **S-Corp:** Pass-through taxation, income flows to personal return
- **LLC:** Pass-through taxation, income flows to personal return
- **Partnership:** Pass-through taxation, allocated to partners
- **Individual:** Direct taxation, standard rates apply

#### Dividend Classifications
- **Qualified Dividends:** Eligible for preferential capital gains rates
- **Ordinary Dividends:** Taxed at ordinary income rates
- **Return of Capital:** Non-taxable, reduces cost basis

### Data Validation Rules

#### Tax Calculation Validation
- Tax categories must match IRS definitions
- All transactions must have federal_taxable and state_taxable flags
- Amounts must be NUMERIC(15,2) for precision
- Tax year cannot be future year
- Quarterly totals must sum to YTD totals

#### Exemption Validation
- Exemption percentages must be between 0.00 and 1.00
- FSIXX exemption rate should be approximately 0.97 (±0.02)
- SPAXX exemption rate should be approximately 0.55 (±0.05) 
- Municipal bond exemptions must be either 0% or 100%

### Test Scenarios

#### Exemption Calculation Tests
```typescript
describe('Tax Exemption Calculations', () => {
  test('FSIXX dividend applies 97% Georgia exemption', () => {
    const dividend = { amount: 1000, symbol: 'FSIXX', type: 'dividend' }
    const result = calculateTax(dividend, 'GA', 2024)
    
    expect(result.federalTaxable).toBe(1000)
    expect(result.stateTaxable).toBeCloseTo(30, 2) // 3% of 1000
    expect(result.exemptAmount).toBeCloseTo(970, 2) // 97% of 1000
  })
  
  test('SPAXX dividend applies 55% Georgia exemption', () => {
    const dividend = { amount: 1000, symbol: 'SPAXX', type: 'dividend' }
    const result = calculateTax(dividend, 'GA', 2024)
    
    expect(result.federalTaxable).toBe(1000)
    expect(result.stateTaxable).toBeCloseTo(450, 2) // 45% of 1000
    expect(result.exemptAmount).toBeCloseTo(550, 2) // 55% of 1000
  })
  
  test('GA municipal bond is double exempt', () => {
    const interest = { amount: 1000, securityType: 'municipal_bond', issuerState: 'GA' }
    const result = calculateTax(interest, 'GA', 2024)
    
    expect(result.federalTaxable).toBe(0)
    expect(result.stateTaxable).toBe(0)
    expect(result.exemptAmount).toBe(1000)
  })
  
  test('Other state municipal is GA taxable', () => {
    const interest = { amount: 1000, securityType: 'municipal_bond', issuerState: 'FL' }
    const result = calculateTax(interest, 'GA', 2024)
    
    expect(result.federalTaxable).toBe(0)
    expect(result.stateTaxable).toBe(1000)
    expect(result.exemptAmount).toBe(0)
  })
  
  test('Consolidated totals equal sum of entity totals', () => {
    const entities = ['entity1', 'entity2', 'entity3']
    const consolidated = calculateConsolidatedTax(entities, 'Q1', 2024)
    const entityTotals = entities.map(id => calculateEntityTax(id, 'Q1', 2024))
    
    const expectedFederal = entityTotals.reduce((sum, e) => sum + e.federalTax, 0)
    const expectedState = entityTotals.reduce((sum, e) => sum + e.stateTax, 0)
    
    expect(consolidated.federalTax).toBeCloseTo(expectedFederal, 2)
    expect(consolidated.stateTax).toBeCloseTo(expectedState, 2)
  })
})
```

---

## Workflow 5: Tax Payment Tracking

**User Story:** "I need to track quarterly estimated tax payments and see what I owe vs what I've paid"

### Tax Payment Center Component
```typescript
interface TaxPaymentData {
  year: number
  quarters: QuarterlyPayment[]
  paymentHistory: PaymentRecord[]
  upcomingPayments: UpcomingPayment[]
  annualSummary: AnnualPaymentSummary
}

interface QuarterlyPayment {
  quarter: 'Q1' | 'Q2' | 'Q3' | 'Q4'
  dueDate: string
  estimated: {
    federal: number
    state: number
  }
  paid: {
    federal: number
    state: number
  }
  status: 'paid' | 'partial' | 'overdue' | 'upcoming'
}

function TaxPaymentTracker({ year }: { year: number }) {
  const { data } = useTaxPayments(year)
  
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Tax Payment Tracker - {year}</CardTitle>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => setYear(year - 1)}>
              {year - 1}
            </Button>
            <Button variant="default">
              {year}
            </Button>
            <Button variant="outline" onClick={() => setYear(year + 1)}>
              {year + 1}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {/* Quarterly Overview Table */}
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Quarter</TableHead>
                <TableHead className="text-right">Fed Est.</TableHead>
                <TableHead className="text-right">Fed Paid</TableHead>
                <TableHead className="text-right">GA Est.</TableHead>
                <TableHead className="text-right">GA Paid</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.quarters.map(quarter => (
                <TableRow key={quarter.quarter}>
                  <TableCell className="font-medium">{quarter.quarter} {year}</TableCell>
                  <TableCell className="text-right">{formatCurrency(quarter.estimated.federal)}</TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end gap-2">
                      {formatCurrency(quarter.paid.federal)}
                      {quarter.paid.federal >= quarter.estimated.federal ? (
                        <CheckCircle className="h-4 w-4 text-green-500" />
                      ) : quarter.paid.federal > 0 ? (
                        <AlertCircle className="h-4 w-4 text-yellow-500" />
                      ) : (
                        <XCircle className="h-4 w-4 text-red-500" />
                      )}
                    </div>
                  </TableCell>
                  <TableCell className="text-right">{formatCurrency(quarter.estimated.state)}</TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end gap-2">
                      {formatCurrency(quarter.paid.state)}
                      {quarter.paid.state >= quarter.estimated.state ? (
                        <CheckCircle className="h-4 w-4 text-green-500" />
                      ) : quarter.paid.state > 0 ? (
                        <AlertCircle className="h-4 w-4 text-yellow-500" />
                      ) : (
                        <XCircle className="h-4 w-4 text-red-500" />
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    <StatusBadge status={quarter.status} />
                  </TableCell>
                </TableRow>
              ))}
              {/* Totals row */}
              <TableRow className="font-medium border-t-2">
                <TableCell>Total</TableCell>
                <TableCell className="text-right">
                  {formatCurrency(data.annualSummary.estimatedFederal)}
                </TableCell>
                <TableCell className="text-right">
                  {formatCurrency(data.annualSummary.paidFederal)}
                </TableCell>
                <TableCell className="text-right">
                  {formatCurrency(data.annualSummary.estimatedState)}
                </TableCell>
                <TableCell className="text-right">
                  {formatCurrency(data.annualSummary.paidState)}
                </TableCell>
                <TableCell>
                  <div className="text-sm">
                    <div>Remaining:</div>
                    <div className="text-red-600">
                      {formatCurrency(data.annualSummary.remaining)}
                    </div>
                  </div>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>
      
      {/* Payment History */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Payment History</CardTitle>
          <Button onClick={() => setShowAddPayment(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Record Payment
          </Button>
        </CardHeader>
        <CardContent>
          <PaymentHistoryTable payments={data.paymentHistory} />
        </CardContent>
      </Card>
      
      {/* Next Payments Due */}
      <Card>
        <CardHeader>
          <CardTitle>Upcoming Payments</CardTitle>
        </CardHeader>
        <CardContent>
          <UpcomingPaymentsList payments={data.upcomingPayments} />
        </CardContent>
      </Card>
    </div>
  )
}
```

### Payment Recording System
```typescript
interface PaymentRecord {
  id: string
  date: string
  entity_id: string
  tax_year: number
  quarter: string
  payment_type: 'federal' | 'state' | 'self_employment'
  amount: number
  payment_method: 'eftps' | 'check' | 'online' | 'wire'
  confirmation_number?: string
  notes?: string
  created_at: string
}

function RecordPaymentDialog({ open, onClose, onSave }: RecordPaymentDialogProps) {
  const [payment, setPayment] = useState<Partial<PaymentRecord>>({
    date: format(new Date(), 'yyyy-MM-dd'),
    tax_year: new Date().getFullYear(),
    quarter: getCurrentQuarter(),
    payment_type: 'federal',
    payment_method: 'eftps'
  })
  
  const handleSave = async () => {
    await onSave({
      ...payment,
      id: generateId(),
      created_at: new Date().toISOString()
    } as PaymentRecord)
    
    onClose()
    setPayment({})
  }
  
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Record Tax Payment</DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Date</Label>
              <Input
                type="date"
                value={payment.date}
                onChange={(e) => setPayment({...payment, date: e.target.value})}
              />
            </div>
            <div>
              <Label>Amount</Label>
              <Input
                type="number"
                step="0.01"
                value={payment.amount || ''}
                onChange={(e) => setPayment({...payment, amount: parseFloat(e.target.value)})}
                placeholder="0.00"
              />
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Tax Year</Label>
              <Select value={payment.tax_year?.toString()} onValueChange={(value) => setPayment({...payment, tax_year: parseInt(value)})}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {[2024, 2023, 2022, 2021].map(year => (
                    <SelectItem key={year} value={year.toString()}>{year}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Quarter</Label>
              <Select value={payment.quarter} onValueChange={(value) => setPayment({...payment, quarter: value})}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Q1">Q1 (Jan-Mar)</SelectItem>
                  <SelectItem value="Q2">Q2 (Apr-Jun)</SelectItem>
                  <SelectItem value="Q3">Q3 (Jul-Sep)</SelectItem>
                  <SelectItem value="Q4">Q4 (Oct-Dec)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Payment Type</Label>
              <Select value={payment.payment_type} onValueChange={(value) => setPayment({...payment, payment_type: value as any})}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="federal">Federal</SelectItem>
                  <SelectItem value="state">Georgia State</SelectItem>
                  <SelectItem value="self_employment">Self-Employment</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Payment Method</Label>
              <Select value={payment.payment_method} onValueChange={(value) => setPayment({...payment, payment_method: value as any})}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="eftps">EFTPS</SelectItem>
                  <SelectItem value="online">Online</SelectItem>
                  <SelectItem value="check">Check</SelectItem>
                  <SelectItem value="wire">Wire Transfer</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          
          <div>
            <Label>Confirmation Number (Optional)</Label>
            <Input
              value={payment.confirmation_number || ''}
              onChange={(e) => setPayment({...payment, confirmation_number: e.target.value})}
              placeholder="Payment confirmation number"
            />
          </div>
          
          <div>
            <Label>Notes (Optional)</Label>
            <Textarea
              value={payment.notes || ''}
              onChange={(e) => setPayment({...payment, notes: e.target.value})}
              placeholder="Additional notes about this payment"
              rows={3}
            />
          </div>
        </div>
        
        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleSave} disabled={!payment.amount || !payment.date}>
            Record Payment
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
```

### Payment Data Queries
```sql
-- Quarterly payment summary
WITH quarterly_estimates AS (
  SELECT 
    EXTRACT(YEAR FROM date) as tax_year,
    'Q' || EXTRACT(QUARTER FROM date) as quarter,
    SUM(federal_tax_estimate) as estimated_federal,
    SUM(state_tax_estimate) as estimated_state
  FROM tax_estimates 
  WHERE tax_year = $year
  GROUP BY EXTRACT(YEAR FROM date), EXTRACT(QUARTER FROM date)
),
quarterly_payments AS (
  SELECT 
    tax_year,
    quarter,
    payment_type,
    SUM(amount) as total_paid
  FROM tax_payments 
  WHERE tax_year = $year
  GROUP BY tax_year, quarter, payment_type
),
payment_summary AS (
  SELECT 
    e.tax_year,
    e.quarter,
    e.estimated_federal,
    e.estimated_state,
    COALESCE(pf.total_paid, 0) as paid_federal,
    COALESCE(ps.total_paid, 0) as paid_state
  FROM quarterly_estimates e
  LEFT JOIN quarterly_payments pf ON e.tax_year = pf.tax_year 
    AND e.quarter = pf.quarter AND pf.payment_type = 'federal'
  LEFT JOIN quarterly_payments ps ON e.tax_year = ps.tax_year 
    AND e.quarter = ps.quarter AND ps.payment_type = 'state'
)
SELECT *,
  CASE 
    WHEN paid_federal >= estimated_federal AND paid_state >= estimated_state THEN 'paid'
    WHEN paid_federal > 0 OR paid_state > 0 THEN 'partial'
    WHEN quarter_due_date < CURRENT_DATE THEN 'overdue'
    ELSE 'upcoming'
  END as status
FROM payment_summary
ORDER BY tax_year, quarter;
```

---

## Workflow 6: Year-Over-Year Comparisons

**User Story:** "I want to see how this year compares to last year"

### YoY Comparison Component
```typescript
interface YoYComparisonData {
  comparisonYears: { current: number; prior: number }
  income: YoYIncomeComparison
  taxes: YoYTaxComparison
  entities: YoYEntityComparison[]
  charts: {
    incomeByQuarter: ChartData[]
    taxLiabilityByQuarter: ChartData[]
    entityPerformance: ChartData[]
  }
}

function YearOverYearComparison({ currentYear, priorYear }: YoYComparisonProps) {
  const { data } = useYoYComparison(currentYear, priorYear)
  
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>
            Year-Over-Year Comparison
            <span className="text-lg font-normal ml-4">
              {currentYear} vs {priorYear}
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {/* Income Comparison */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Income Comparison (All Entities)</h3>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Category</TableHead>
                  <TableHead className="text-right">{currentYear} YTD</TableHead>
                  <TableHead className="text-right">{priorYear} YTD</TableHead>
                  <TableHead className="text-right">Change</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow>
                  <TableCell className="font-medium">Dividend Income</TableCell>
                  <TableCell className="text-right">{formatCurrency(data.income.current.dividends)}</TableCell>
                  <TableCell className="text-right">{formatCurrency(data.income.prior.dividends)}</TableCell>
                  <TableCell className="text-right">
                    <ChangeIndicator 
                      current={data.income.current.dividends}
                      prior={data.income.prior.dividends}
                    />
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell className="font-medium">Interest Income</TableCell>
                  <TableCell className="text-right">{formatCurrency(data.income.current.interest)}</TableCell>
                  <TableCell className="text-right">{formatCurrency(data.income.prior.interest)}</TableCell>
                  <TableCell className="text-right">
                    <ChangeIndicator 
                      current={data.income.current.interest}
                      prior={data.income.prior.interest}
                    />
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell className="font-medium">Capital Gains</TableCell>
                  <TableCell className="text-right">{formatCurrency(data.income.current.capitalGains)}</TableCell>
                  <TableCell className="text-right">{formatCurrency(data.income.prior.capitalGains)}</TableCell>
                  <TableCell className="text-right">
                    <ChangeIndicator 
                      current={data.income.current.capitalGains}
                      prior={data.income.prior.capitalGains}
                    />
                  </TableCell>
                </TableRow>
                <TableRow className="font-medium border-t">
                  <TableCell>Total Income</TableCell>
                  <TableCell className="text-right">{formatCurrency(data.income.current.total)}</TableCell>
                  <TableCell className="text-right">{formatCurrency(data.income.prior.total)}</TableCell>
                  <TableCell className="text-right">
                    <ChangeIndicator 
                      current={data.income.current.total}
                      prior={data.income.prior.total}
                    />
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </div>
          
          {/* Tax Comparison */}
          <div className="space-y-4 mt-8">
            <h3 className="text-lg font-semibold">Tax Liability Comparison</h3>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Tax Type</TableHead>
                  <TableHead className="text-right">{currentYear} Est</TableHead>
                  <TableHead className="text-right">{priorYear} Actual</TableHead>
                  <TableHead className="text-right">Change</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow>
                  <TableCell className="font-medium">Federal Tax</TableCell>
                  <TableCell className="text-right">{formatCurrency(data.taxes.current.federal)}</TableCell>
                  <TableCell className="text-right">{formatCurrency(data.taxes.prior.federal)}</TableCell>
                  <TableCell className="text-right">
                    <ChangeIndicator 
                      current={data.taxes.current.federal}
                      prior={data.taxes.prior.federal}
                    />
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell className="font-medium">Georgia Tax</TableCell>
                  <TableCell className="text-right">{formatCurrency(data.taxes.current.state)}</TableCell>
                  <TableCell className="text-right">{formatCurrency(data.taxes.prior.state)}</TableCell>
                  <TableCell className="text-right">
                    <ChangeIndicator 
                      current={data.taxes.current.state}
                      prior={data.taxes.prior.state}
                    />
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell className="font-medium">Effective Rate</TableCell>
                  <TableCell className="text-right">{(data.taxes.current.effectiveRate * 100).toFixed(1)}%</TableCell>
                  <TableCell className="text-right">{(data.taxes.prior.effectiveRate * 100).toFixed(1)}%</TableCell>
                  <TableCell className="text-right">
                    <span className={cn(
                      "flex items-center gap-1",
                      data.taxes.current.effectiveRate > data.taxes.prior.effectiveRate 
                        ? "text-red-600" : "text-green-600"
                    )}>
                      {data.taxes.current.effectiveRate > data.taxes.prior.effectiveRate ? (
                        <TrendingUp className="h-4 w-4" />
                      ) : (
                        <TrendingDown className="h-4 w-4" />
                      )}
                      {Math.abs((data.taxes.current.effectiveRate - data.taxes.prior.effectiveRate) * 100).toFixed(1)}%
                    </span>
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
      
      {/* Charts */}
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Quarterly Income Comparison</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={data.charts.incomeByQuarter}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="quarter" />
                <YAxis />
                <Tooltip formatter={(value) => formatCurrency(value)} />
                <Bar dataKey="current" fill="#3b82f6" name={currentYear.toString()} />
                <Bar dataKey="prior" fill="#64748b" name={priorYear.toString()} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Tax Liability by Quarter</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={data.charts.taxLiabilityByQuarter}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="quarter" />
                <YAxis />
                <Tooltip formatter={(value) => formatCurrency(value)} />
                <Line 
                  type="monotone" 
                  dataKey="current" 
                  stroke="#3b82f6" 
                  name={`${currentYear} Tax`}
                  strokeWidth={3}
                />
                <Line 
                  type="monotone" 
                  dataKey="prior" 
                  stroke="#64748b" 
                  name={`${priorYear} Tax`}
                  strokeWidth={2}
                  strokeDasharray="5 5"
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
```

### Change Indicator Component
```typescript
interface ChangeIndicatorProps {
  current: number
  prior: number
  format?: 'currency' | 'percentage' | 'number'
  inverse?: boolean // true if decrease is good (e.g., taxes)
}

function ChangeIndicator({ current, prior, format = 'currency', inverse = false }: ChangeIndicatorProps) {
  const change = current - prior
  const percentChange = prior !== 0 ? (change / prior) * 100 : 0
  const isPositive = change > 0
  const isGood = inverse ? !isPositive : isPositive
  
  const formatValue = (value: number) => {
    switch (format) {
      case 'currency': return formatCurrency(value)
      case 'percentage': return `${value.toFixed(1)}%`
      case 'number': return value.toLocaleString()
      default: return value.toString()
    }
  }
  
  return (
    <span className={cn(
      "flex items-center gap-1 font-medium",
      isGood ? "text-green-600" : "text-red-600"
    )}>
      {isPositive ? (
        <TrendingUp className="h-4 w-4" />
      ) : (
        <TrendingDown className="h-4 w-4" />
      )}
      <span>
        {isPositive ? '+' : ''}{formatValue(change)}
      </span>
      <span className="text-xs text-muted-foreground">
        ({percentChange > 0 ? '+' : ''}{percentChange.toFixed(1)}%)
      </span>
    </span>
  )
}
```

## Implementation Guidelines

### Tax Calculation Precision
- Use NUMERIC(15,2) for all monetary values
- Round to nearest cent using standard rounding rules
- Validate all calculations against known tax software results
- Store exemption rates as exact decimals (0.97, not 97%)

### Multi-Entity Aggregation
- Aggregate at SQL level for performance
- Handle pass-through entity taxation correctly
- Ensure entity isolation in calculations
- Support filtering by entity selection

### Export Functionality
```typescript
interface TaxExportOptions {
  format: 'csv' | 'pdf' | 'quickbooks' | 'turbotax' | 'proseries'
  period: TaxPeriod
  entities: string[]
  includeDetails: boolean
  includeDocuments: boolean
}

async function exportTaxData(options: TaxExportOptions): Promise<Blob> {
  const taxData = await aggregateTaxData(options.period, options.entities)
  
  switch (options.format) {
    case 'csv':
      return generateCSVExport(taxData, options)
    case 'pdf':
      return generatePDFReport(taxData, options)
    case 'quickbooks':
      return generateQBOExport(taxData, options)
    case 'turbotax':
      return generateTurboTaxExport(taxData, options)
    case 'proseries':
      return generateProSeriesExport(taxData, options)
    default:
      throw new Error(`Unsupported export format: ${options.format}`)
  }
}
```

### Performance Optimizations
- Cache tax calculations for frequently accessed periods
- Use materialized views for complex aggregations
- Implement proper database indexes on tax-related fields
- Batch process exemption calculations

---

*This guide provides complete context for tax workflow implementation. All calculation rules, exemption logic, and reporting features are specified for autonomous development.*