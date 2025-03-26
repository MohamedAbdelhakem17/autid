import requests
from bs4 import BeautifulSoup
from datetime import datetime


class SEOTechnicalAnalyzer:
    def __init__(self, url: str):
        self.url = url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.issues = []
        self.warnings = []
        self.info = []

    def analyze(self):
        try:
            response = requests.get(self.url, headers=self.headers)
            response.raise_for_status()
            self.soup = BeautifulSoup(response.text, "html.parser")

            self._analyze_images()
            self._analyze_canonical()
            self._analyze_schema()

            return self._generate_report()
        except requests.RequestException as e:
            return {"error": f"Failed to fetch URL: {str(e)}"}

    def _analyze_images(self):
        images = self.soup.find_all("img")
        missing_alt = [
            img.get("src", "unknown") for img in images if not img.get("alt")
        ]

        if missing_alt:
            self.issues.append(
                {
                    "category": "Image Optimization",
                    "issue": f"Missing alt text on {len(missing_alt)} images",
                    "impact": "High - Alt text is crucial for accessibility and image SEO",
                    "recommendation": "Add descriptive alt text to all images",
                }
            )

    def _analyze_canonical(self):
        canonical = self.soup.find("link", {"rel": "canonical"})
        if canonical and canonical.get("href") and canonical["href"] != self.url:
            self.warnings.append(
                {
                    "category": "Canonical Tag",
                    "issue": f"Canonical URL ({canonical['href']}) differs from current URL",
                    "impact": "Medium - May indicate content duplication or incorrect configuration",
                    "recommendation": "Verify canonical URL is correct",
                }
            )

    def _analyze_schema(self):
        schema_scripts = self.soup.find_all("script", {"type": "application/ld+json"})
        if not schema_scripts:
            self.warnings.append(
                {
                    "category": "Structured Data",
                    "issue": "No schema.org structured data found",
                    "impact": "Medium - Structured data helps search engines understand content",
                    "recommendation": "Add relevant schema.org markup for your content type",
                }
            )

    def _generate_report(self):
        return {
            "report": f"=== SEO Technical Analysis Report for {self.url} ===",
            "critical_issues": [],
            "high_impact_issues": [
                issue for issue in self.issues if "High" in issue.get("impact", "")
            ],
            "warnings": self.warnings,
            "total_issues": len(self.issues),
            "total_warnings": len(self.warnings),
        }
