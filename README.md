# 🔐 Password Intelligence System (Multi-Model ML App)

This project is a **multi-model machine learning–based password analysis system** that evaluates password security, improves weak passwords, and provides intelligent recommendations.
All decisions are made using **trained machine learning models** combined with rule-based heuristics.

## 🚀 Quick Start

### Local Development
```bash
# Install dependencies
pip install -r requirements-consolidated.txt

# Run the Flask app
cd password-ml-app
python app.py
```

Visit `http://localhost:5000` in your browser.

### Docker
```bash
# Build and run with Docker
docker build -t password-assistant .
docker run -p 5000:5000 password-assistant
```

### Production Deployment
See **[DEPLOYMENT.md](DEPLOYMENT.md)** for detailed deployment instructions for:
- ✅ **Render** (Recommended)
- ✅ Railway
- ✅ Heroku
- ✅ Docker (AWS/GCP/DigitalOcean)
- ⚠️ Vercel (Serverless - advanced)

## 📡 API Endpoints

### `GET /health`
Health check endpoint for monitoring.
```bash
curl https://your-app.com/health
```
Response: `{"status": "healthy", "service": "password-assistant"}`

### `POST /api/analyze`
Analyze a password and get strength prediction, issues, and suggestions.
```bash
curl -X POST https://your-app.com/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"password": "MyPassword123!"}'
```

Response:
```json
{
  "input_password": "MyPassword123!",
  "predicted_strength": "Strong",
  "issues_found": [],
  "suggestions": ["!321drowssaPyM@1A", "!321drowssaP#X", "MyPassword123!_Strong"],
  "estimated_crack_time": "1234 years"
}
```

## 🧠 Machine Learning Models Used

The system integrates **multiple independent ML models**, each responsible for a specific task in password intelligence.

### 1️⃣ Password Strength Prediction Model

**Files used**

- `enhanced_password_model_1.pkl`
- `tfidf_vectorizer_1.pkl`

**Purpose**
Predicts the **overall strength of a password**.

**How it works**

- The password is converted into numerical features using **TF-IDF vectorization**
- The trained classification model predicts:

  * `Weak`
  * `Medium`
  * `Strong`

**Output example**

```
Input: koyel@123!RAM
Predicted Strength: Medium
```

### 2️⃣ Password Improvement Model

**File used**

- `password_improvement_model.pkl`

**Purpose**
Generates a **stronger version of the input password**.

**How it works**

- Uses the same vectorized representation of the password
- Predicts an improved password with:

  * Higher complexity
  * Better character distribution
  * Increased resistance to attacks

**Output example**

```
Original Password: koyel
Improved Password: Ekoyel?,^2u/
```

### 3️⃣ Password Length Recommendation Model

**Files used**

- `length_recommender_model.pkl`
- `length_vectorizer.pkl`

**Purpose**
Predicts the **optimal password length** for better security.

**How it works**

- Analyzes the structure and patterns of the input password
- Outputs a **recommended length** that improves password strength

**Output example**

```
Current Length: 7
Recommended Length: 14
```

### 4️⃣ Advanced Password Recommendation Model

**Files used**

- `new_recommender_model.pkl`
- `new_vectorizer.pkl`

**Purpose**
Generates **additional strong password suggestions**.

**How it works**

- Uses a separate ML pipeline trained on strong-password patterns
- Produces multiple alternative secure passwords

**Output example**

```
ML Suggestions:
- jmR6%MNAQM'S
- |I-83o6JJ^Wk
- ig7//tiQ+J2h
```

## 🔄 How All Models Work Together

1. User enters a password
2. Password is processed by **multiple ML pipelines**
3. The system returns:

   * Predicted password strength
   * Improved password
   * Recommended password length
   * Additional ML-generated suggestions

All outputs are generated using **trained machine learning models** combined with rule-based heuristics for optimal results.

## 🛠️ Tech Stack

* Python 3.12
* Flask (Web Framework)
* Scikit-learn (Machine Learning)
* Joblib (Model Serialization)
* TF-IDF Vectorization
* Gunicorn (WSGI Server)
* Docker (Containerization)
* GitHub Actions (CI/CD)

## 🧪 Testing

Run the test suite:
```bash
# Install test dependencies
pip install -r requirements-consolidated.txt

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=password-ml-app --cov-report=term-missing
```

## 🔄 CI/CD

This project uses GitHub Actions for continuous integration and deployment:
- ✅ Automated testing on every push/PR
- ✅ Docker image builds and validation
- ✅ Code quality checks (flake8)
- ✅ Health endpoint verification

See `.github/workflows/ci.yml` for the full CI/CD pipeline.

## 📚 Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete deployment guide for all platforms
- **[tests/test_app.py](tests/test_app.py)** - Unit and integration tests
- **[.github/workflows/ci.yml](.github/workflows/ci.yml)** - CI/CD pipeline configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests to ensure everything works (`pytest tests/`)
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📝 License

This project is open source and available under the terms specified in the LICENSE file.

## 🔗 Links

- **Live Demo**: (Deploy to Render/Railway and add your link here)
- **Issues**: [GitHub Issues](https://github.com/koyeliya2004/checking-password-strength-ml/issues)
- **Discussions**: [GitHub Discussions](https://github.com/koyeliya2004/checking-password-strength-ml/discussions)

---

**Made with ❤️ by koyeliya2004**

