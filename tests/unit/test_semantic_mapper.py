from app.semantic_layer.synonym_mapper import (
    normalize_metric_terms,
    normalize_region,
    normalize_segment,
    normalize_time_period,
    detect_forbidden_confusions,
)
from app.semantic_layer.semantic_parser import SemanticParser


class TestSynonymMapper:
    def test_normalize_metric_revenue(self):
        result = normalize_metric_terms("show me revenue")
        assert "revenue" in result.values()

    def test_normalize_metric_sales(self):
        result = normalize_metric_terms("sales in Q1")
        assert "revenue" in result.values()

    def test_normalize_metric_churn(self):
        result = normalize_metric_terms("customer loss rate")
        assert "churn" in result.values()

    def test_normalize_region_apac(self):
        result = normalize_region("data for APAC")
        assert "APAC" in result.values()

    def test_normalize_region_emea(self):
        result = normalize_region("europe revenue")
        assert "EMEA" in result.values()

    def test_normalize_segment_enterprise(self):
        result = normalize_segment("enterprise customers")
        assert "Enterprise" in result.values()

    def test_normalize_segment_smb(self):
        result = normalize_segment("smb segment")
        assert "SMB" in result.values()

    def test_normalize_time_q1(self):
        result = normalize_time_period("Q1 results")
        assert "Q1_2025" in result.values()

    def test_normalize_time_last_quarter(self):
        result = normalize_time_period("last quarter performance")
        assert "Q4_2025" in result.values()

    def test_forbidden_confusion(self):
        warnings = detect_forbidden_confusions(
            "revenue bookings pipeline"
        )
        assert len(warnings) >= 1

    def test_no_forbidden_confusion(self):
        warnings = detect_forbidden_confusions("revenue in APAC")
        assert len(warnings) == 0

    def test_metric_attrition(self):
        result = normalize_metric_terms("attrition rate")
        assert "churn" in result.values()

    def test_metric_marketing_spend(self):
        result = normalize_metric_terms("marketing spend")
        assert "marketing_spend" in result.values()

    def test_metric_support_tickets(self):
        result = normalize_metric_terms("support tickets")
        assert "support_tickets" in result.values()

    def test_metric_product_usage(self):
        result = normalize_metric_terms("product usage")
        assert "product_usage" in result.values()

    def test_region_latam(self):
        result = normalize_region("latam revenue")
        assert "LATAM" in result.values()

    def test_segment_midmarket(self):
        result = normalize_segment("mid-market clients")
        assert "Mid-Market" in result.values()


class TestSemanticParser:
    def setup_method(self):
        self.parser = SemanticParser()

    def test_basic_parse(self):
        result = self.parser.parse("revenue in APAC")
        assert result["original_query"] == "revenue in APAC"
        assert "revenue" in result["metrics"]
        assert result["filters"].get("region") == "APAC"
        assert "canonical_query" in result

    def test_parse_with_mapped_terms(self):
        result = self.parser.parse("sales in APAC for enterprise customers")
        assert "revenue" in result["mapped_terms"].values()
        assert result["mapped_terms"].get("enterprise customers") == "Enterprise"

    def test_parse_complex(self):
        result = self.parser.parse(
            "why did churn increase in EMEA for SMB last quarter"
        )
        assert "churn" in result["metrics"]
        assert result["filters"].get("region") == "EMEA"
        assert result["filters"].get("segment") == "SMB"

    def test_parse_no_metrics(self):
        result = self.parser.parse("what is the definition of pipeline")
        assert "sales_pipeline" in result["metrics"]
        assert "pipeline" in result["mapped_terms"]
