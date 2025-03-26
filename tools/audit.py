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

            # Run all analysis methods
            self._analyze_title()
            self._analyze_meta_description()
            self._analyze_headings()
            self._analyze_images()
            self._analyze_canonical()
            self._analyze_robots()
            self._analyze_schema()
            self._analyze_performance()
            self._analyze_mobile_friendliness()
            self._analyze_ssl()

            return self._generate_report()

        except requests.RequestException as e:
            return {"error": f"Failed to fetch URL: {str(e)}"}

    # Analysis page Title
    def _analyze_title(self):
        title = self.soup.title.string if self.soup.title else None

        if not title:
            self.issues.append(
                {
                    "category": "Title Tag",
                    "issue": "Missing title tag",
                    "impact": "Critical - Title tags are crucial for SEO and user experience",
                    "recommendation": "Add a descriptive title tag between 30-60 characters",
                }
            )
        else:
            length = len(title)
            if length < 30:
                self.issues.append(
                    {
                        "category": "Title Tag",
                        "issue": f"Title too short ({length} characters): {title}",
                        "impact": "High - Short titles may not be descriptive enough for search engines and users",
                        "recommendation": "Expand title to be between 30-60 characters",
                    }
                )
            elif length > 60:
                self.issues.append(
                    {
                        "category": "Title Tag",
                        "issue": f"Title too long ({length} characters): {title}",
                        "impact": "Medium - Long titles will be truncated in search results",
                        "recommendation": "Reduce title length to be between 30-60 characters",
                    }
                )

    # Analysis Meta Description
    def _analyze_meta_description(self):
        """Analyze meta description"""
        meta_desc = self.soup.find("meta", {"name": "description"})

        if not meta_desc:
            self.issues.append(
                {
                    "category": "Meta Description",
                    "issue": "Missing meta description",
                    "impact": "High - Meta descriptions are important for CTR in search results",
                    "recommendation": "Add a compelling meta description between 70-155 characters",
                }
            )
        elif meta_desc.get("content"):
            length = len(meta_desc["content"])
            if length < 70:
                self.warnings.append(
                    {
                        "category": "Meta Description",
                        "issue": f"Description too short ({length} characters)",
                        "impact": "Medium - Short descriptions may not provide enough context",
                        "recommendation": "Expand description to be between 70-155 characters",
                    }
                )
            elif length > 155:
                self.warnings.append(
                    {
                        "category": "Meta Description",
                        "issue": f"Description too long ({length} characters)",
                        "impact": "Low - Long descriptions will be truncated in search results",
                        "recommendation": "Reduce description length to be between 70-155 characters",
                    }
                )

    # Analysis Headings
    def _analyze_headings(self):

        headings = []
        for i in range(1, 7):
            h_tags = self.soup.find_all(f"h{i}")
            headings.extend([(f"h{i}", h.text.strip()) for h in h_tags])

        if not any(h[0] == "h1" for h in headings):
            self.issues.append(
                {
                    "category": "Heading Structure",
                    "issue": "Missing H1 heading",
                    "impact": "High - H1 is a crucial signal for page topic and structure",
                    "recommendation": "Add a single, descriptive H1 heading",
                }
            )

        h1_count = len([h for h in headings if h[0] == "h1"])
        if h1_count > 1:
            self.warnings.append(
                {
                    "category": "Heading Structure",
                    "issue": f"Multiple H1 headings found ({h1_count})",
                    "impact": "Medium - Multiple H1s can confuse page hierarchy",
                    "recommendation": "Use only one H1 heading per page",
                }
            )

        prev_level = 0
        for h_tag, text in headings:
            current_level = int(h_tag[1])
            if current_level - prev_level > 1:
                self.warnings.append(
                    {
                        "category": "Heading Structure",
                        "issue": f"Skipped heading level (from H{prev_level} to H{current_level})",
                        "impact": "Medium - Improper heading hierarchy affects accessibility and SEO",
                        "recommendation": "Maintain proper heading hierarchy (H1 → H2 → H3)",
                    }
                )
            prev_level = current_level

    # Analysis Image Optimization
    def _analyze_images(self):
        images = self.soup.find_all("img")
        missing_alt = [
            img.get("src", "unknown") for img in images if not img.get("alt")
        ]
        large_images = [
            img["src"]
            for img in images
            if img.get("width")
            and img.get("height")
            and img["width"].isdigit()
            and img["height"].isdigit()
            and (int(img["width"]) > 1000 or int(img["height"]) > 1000)
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

        if large_images:
            self.issues.append(
                {
                    "category": "Image Optimization",
                    "issue": f"Found {len(large_images)} images exceeding 1000px in width or height",
                    "impact": "Medium - Large images can slow down page load times",
                    "recommendation": "Optimize large images by resizing or compressing them",
                }
            )

    # Analysis Canonical Tag
    def _analyze_canonical(self):
        canonical = self.soup.find("link", {"rel": "canonical"})
        if canonical:
            self.issues.append(
                {
                    "category": "Canonical Tag",
                    "issue": "Missing canonical tag",
                    "impact": "High - Canonical tags help prevent duplicate content issues",
                    "recommendation": "Add a canonical tag pointing to the preferred URL",
                }
            )
        elif canonical.get("href"):
            canonical_url = canonical["href"]
            if canonical_url != self.url:
                self.warnings.append(
                    {
                        "category": "Canonical Tag",
                        "issue": f"Canonical URL ({canonical_url}) differs from current URL",
                        "impact": "Medium - May indicate content duplication or incorrect configuration",
                        "recommendation": "Verify canonical URL is correct",
                    }
                )

    # Analysis Robots Meta Tag
    def _analyze_robots(self):
        robots_meta = self.soup.find("meta", {"name": "robots"}) or self.soup.find(
            "meta", {"name": "googlebot"}
        )

        if not robots_meta:
            self.warnings.append(
                {
                    "category": "Robots Meta",
                    "issue": "Missing robots meta tag",
                    "impact": "Low - Default behavior allows indexing and following",
                    "recommendation": "Consider adding robots meta tag for explicit control",
                }
            )
        else:
            content = robots_meta.get("content", "").lower()
            if "noindex" in content:
                self.issues.append(
                    {
                        "category": "Robots Meta",
                        "issue": "Page is set to noindex",
                        "impact": "Critical - Page will not be indexed by search engines",
                        "recommendation": "Remove noindex if page should be indexed",
                    }
                )
            if "nofollow" in content:
                self.warnings.append(
                    {
                        "category": "Robots Meta",
                        "issue": "Page is set to nofollow",
                        "impact": "High - Links on page won't pass authority",
                        "recommendation": "Remove nofollow if links should be followed",
                    }
                )

    # Analysis Schema.org Structured Data
    def _analyze_schema(self):
        schema_scripts = self.soup.find_all("script", {"type": "application/ld+json"})
        schema_found = "schema.org" in str(self.soup)

        if not schema_found and not schema_scripts:
            self.warnings.append(
                {
                    "category": "Structured Data",
                    "issue": "No schema.org structured data found",
                    "impact": "Medium - Structured data helps search engines understand content",
                    "recommendation": "Add relevant schema.org markup for your content type",
                }
            )
        else:
            self.info.append(
                {
                    "category": "Structured Data",
                    "message": f"Found {len(schema_scripts)} schema.org scripts",
                }
            )

    # Analysis Page Performance
    def _analyze_performance(self):
        page_size = len(str(self.soup))
        if page_size > 100000:  # 100KB
            self.warnings.append(
                {
                    "category": "Performance",
                    "issue": f"Large page size ({page_size/1000:.1f}KB)",
                    "impact": "Medium - Large pages load slower and may affect Core Web Vitals",
                    "recommendation": "Optimize page size by minimizing HTML, CSS, and JavaScript",
                }
            )

    # Check basic mobile-friendliness indicators
    def _analyze_mobile_friendliness(self):
        viewport = self.soup.find("meta", {"name": "viewport"})
        if not viewport:
            self.issues.append(
                {
                    "category": "Mobile Optimization",
                    "issue": "Missing viewport meta tag",
                    "impact": "High - Page may not be mobile-friendly",
                    "recommendation": "Add proper viewport meta tag for mobile devices",
                }
            )

    # Check SSL/HTTPS implementation
    def _analyze_ssl(self):
        if not self.url.startswith("https"):
            self.issues.append(
                {
                    "category": "Security",
                    "issue": "Not using HTTPS",
                    "impact": "High - HTTPS is a ranking factor and security requirement",
                    "recommendation": "Implement SSL/HTTPS on your website",
                }
            )

    # Generate final report 
    def _generate_report(self):
        return {
            "report": f"SEO Technical Analysis Report for {self.url} ",
            "url": self.url,
            "scan_date": datetime.now().isoformat(),
            "critical_issues": [
                issue for issue in self.issues if "Critical" in issue.get("impact", "")
            ],
            "high_impact_issues": [
                issue for issue in self.issues if "High" in issue.get("impact", "")
            ],
            "warnings": self.warnings,
            "info": self.info,
            "total_issues": len(self.issues),
            "total_warnings": len(self.warnings),
        }
