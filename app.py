from flask import Flask, request, jsonify

# tools
from tools.audit import SEOTechnicalAnalyzer

app = Flask(__name__)


@app.route("/analyze", methods=["GET", "POST"])
def analyze_website():
    url = request.args.get("url") or request.json.get("url")
    if not url:
        return jsonify({"error": "URL parameter is required"}), 400
    analyzer = SEOTechnicalAnalyzer(url)
    results = analyzer.analyze()
    return jsonify(results)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
