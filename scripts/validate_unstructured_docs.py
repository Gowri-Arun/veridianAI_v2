import os
import yaml

REQUIRED_DOCS = [
    "kpi_definitions", "schema_definitions", "regional_taxonomy",
    "q1_business_review", "q2_business_review", "q3_business_review", "q4_business_review",
    "q4_apac_revenue_report", "pricing_change_memo", "marketing_campaign_memo",
    "support_escalation_report", "product_release_notes", "customer_success_notes",
    "emea_pipeline_review", "smb_churn_review", "enterprise_retention_notes",
    "flowops_release_incident", "sales_cycle_review", "customer_segment_guide",
    "known_metric_confusions"
]

REQUIRED_FIELDS = [
    "doc_id", "title", "doc_type", "quarter", "region", "segment", "related_metrics", "source"
]

def main():
    print("--- STARTING UNSTRUCTURED DOCS VALIDATION ---")
    
    unstructured_dir = "data/raw/unstructured"
    if not os.path.exists(unstructured_dir):
        print(f"[FAIL] Directory '{unstructured_dir}' does not exist.")
        exit(1)
        
    errors = 0
    validated_count = 0
    
    for doc_name in REQUIRED_DOCS:
        filename = f"{doc_name}.md"
        filepath = os.path.join(unstructured_dir, filename)
        
        # 1. Check file exists
        if not os.path.exists(filepath):
            print(f"[FAIL] File missing: {filepath}")
            errors += 1
            continue
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 2. Check frontmatter presence
        if not content.startswith("---"):
            print(f"[FAIL] {filename} does not start with frontmatter marker '---'")
            errors += 1
            continue
            
        parts = content.split("---", 2)
        if len(parts) < 3:
            print(f"[FAIL] {filename} does not have closed frontmatter '---'")
            errors += 1
            continue
            
        frontmatter_str = parts[1]
        body = parts[2].strip()
        
        # 3. Check non-empty body
        if not body:
            print(f"[FAIL] {filename} has an empty body.")
            errors += 1
            continue
            
        # 4. Check frontmatter fields
        try:
            metadata = yaml.safe_load(frontmatter_str)
        except Exception as e:
            print(f"[FAIL] {filename} has invalid YAML frontmatter: {e}")
            errors += 1
            continue
            
        for field in REQUIRED_FIELDS:
            if field not in metadata:
                print(f"[FAIL] {filename} is missing metadata field: '{field}'")
                errors += 1
                
        # 5. Check doc_id matches filename
        if metadata.get("doc_id") != doc_name:
            print(f"[FAIL] {filename} doc_id '{metadata.get('doc_id')}' does not match filename.")
            errors += 1
            
        # 6. Check for the restricted legacy project name.
        restricted_keyword = "Analyst" + "Graph"
        if restricted_keyword in content:
            print(f"[FAIL] {filename} contains restricted keyword")
            errors += 1
            
        validated_count += 1
        
    print(f"Validated {validated_count} / {len(REQUIRED_DOCS)} files.")
    
    if errors == 0:
        print("\n*** ALL UNSTRUCTURED DOCS VALIDATED SUCCESSFULLY! ***")
    else:
        print(f"\n!!! FAILED VALIDATION: {errors} errors found.")
        exit(1)

if __name__ == "__main__":
    main()
