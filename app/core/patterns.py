import re

FILTER_PATTERNS: list[tuple[str, str, str]] = [
    (r"\bapac\b|\basia[\s-]?pacific\b", "region", "APAC"),
    (r"\bemea\b|\beurope\b", "region", "EMEA"),
    (r"\bnorth america\b|\bna\b", "region", "North America"),
    (r"\blatam\b", "region", "LATAM"),
    (r"\benterprise\b|\blarge customers?\b|\benterprise clients?\b", "segment", "Enterprise"),
    (r"\bsmb\b|\bsmall business\b|\bsmall and medium\b", "segment", "SMB"),
    (r"\bmid[\s-]?market\b|\bmidmarket\b", "segment", "Mid-Market"),
    (r"\bq1\b", "quarter", "Q1_2025"),
    (r"\bq2\b", "quarter", "Q2_2025"),
    (r"\bq3\b", "quarter", "Q3_2025"),
    (r"\bq4\b", "quarter", "Q4_2025"),
    (r"\blast quarter\b", "quarter", "Q4_2025"),
    (r"\bprevious quarter\b", "quarter", "Q3_2025"),
]
