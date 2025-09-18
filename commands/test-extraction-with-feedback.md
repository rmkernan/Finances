# Test Extraction with Detailed Feedback

**Created:** 09/18/25 11:50AM ET
**Purpose:** Prompt template for testing document extraction with comprehensive feedback

## Prompt for Sonnet-Task Agent

Please perform a document extraction test with special focus on providing detailed feedback about the process, instructions, and any challenges encountered.

### Primary Task
Execute the document processing workflow in `/commands/process-inbox.md` for any documents in `/documents/inbox/`.

### CRITICAL: Provide Detailed Feedback

As you work, document the following:

#### 1. Instruction Clarity
- Which instructions were crystal clear?
- Which parts were ambiguous or confusing?
- Did you have to make assumptions? What were they?
- Were there conflicting instructions between different documents?

#### 2. Process Observations
- What worked smoothly?
- Where did you encounter friction?
- What decisions did you have to make that weren't covered in the instructions?
- Did the actual document structure match what the instructions prepared you for?

#### 3. Unexpected Encounters
- What surprised you in the document content?
- Were there data patterns not covered in the guides?
- Did you find transaction types or formats not documented?
- Were there edge cases the instructions didn't address?

#### 4. Questions and Clarifications Needed
- What specific questions arose during extraction?
- What additional context would have helped?
- Which business rules were unclear?
- What entity/account mappings were ambiguous?

#### 5. Improvement Suggestions
- How could the instructions be clearer?
- What additional patterns should be documented?
- What validation rules would catch potential errors?
- How could the JSON structure be improved?

### Extraction Requirements

1. **Extract EXACTLY what you see** - no interpretation or categorization
2. **Use the simplified JSON structure** from process-inbox.md
3. **Document every assumption** in the extraction_feedback section
4. **Flag every ambiguity** rather than guessing
5. **Include page numbers** for every extracted item

### Expected Output

1. **JSON extraction file** in `/documents/extractions/`
2. **Detailed feedback report** addressing all points above
3. **Specific examples** of any issues encountered
4. **Line-by-line critique** of unclear instructions

### What NOT to Do
- Don't apply tax rules or categorization
- Don't move files from inbox
- Don't load to database
- Don't make entity mappings without explicit data

### Success Metrics
Your extraction is successful if:
- Every transaction in the document is captured
- Account holders are exactly as shown
- All ambiguities are documented
- Feedback is specific and actionable

Please be brutally honest about what worked and what didn't. Your feedback will directly improve our process.