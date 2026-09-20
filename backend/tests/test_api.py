"""Unit and API Integration Tests for Fake News Detection Backend.

Tests endpoints, input validations, edge cases, error conditions,
token attribution schemas, and benchmark data.
"""

from __future__ import annotations

from backend.app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_healthz_endpoint():
    """Verify liveness probe returns HTTP 200 and healthy status."""
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "X-Process-Time" in response.headers


def test_readyz_endpoint():
    """Verify readiness probe returns HTTP 200 and initialized engines."""
    response = client.get("/readyz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert "bilstm" in data["engines"]
    assert "bert" in data["engines"]


def test_predict_lstm_credible():
    """Verify LSTM endpoint correctly evaluates credible financial news."""
    payload = {
        "title": "Federal Reserve Liquidity Announcement",
        "text": "The Federal Reserve and peer central banks announced coordinated liquidity swap lines.",
        "model": "lstm",
    }
    response = client.post("/api/predict/lstm", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["modelId"] == "lstm"
    assert data["verdict"] in ("REAL", "FAKE", "UNCERTAIN")
    assert 0.0 <= data["confidence"] <= 1.0
    assert 0.0 <= data["probabilityFake"] <= 1.0
    assert 0.0 <= data["probabilityReal"] <= 1.0
    assert len(data["saliencyTokens"]) > 0
    first_token = data["saliencyTokens"][0]
    assert "id" in first_token
    assert "token" in first_token
    assert first_token["direction"] in ("real", "fake", "neutral")
    assert 0.0 <= first_token["weight"] <= 1.0


def test_predict_bert_clickbait():
    """Verify BERT endpoint correctly evaluates sensational clickbait content."""
    payload = {
        "title": "SHOCKING SECRET CURE",
        "text": "Shocking secret miracle cure that big pharma doctors beg you not to see!",
        "model": "bert",
    }
    response = client.post("/api/predict/bert", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["modelId"] == "bert"
    assert data["verdict"] == "FAKE"
    assert data["probabilityFake"] > 0.60
    assert len(data["saliencyTokens"]) > 0
    fake_tokens = [t for t in data["saliencyTokens"] if t["direction"] == "fake"]
    assert len(fake_tokens) > 0


def test_predict_both_comparison():
    """Verify dual-model comparison endpoint returns consensus and both model outputs."""
    payload = {
        "title": "Apollo 11 Secret",
        "text": "Secret glow-in-the-dark moon sticker conspiracy leaked by whistleblower.",
        "model": "both",
    }
    response = client.post("/api/predict/both", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["targetModel"] == "both"
    assert data["lstm"] is not None
    assert data["bert"] is not None
    assert data["lstm"]["modelId"] == "lstm"
    assert data["bert"]["modelId"] == "bert"
    assert data["consensus"] in ("AGREEMENT", "DIVERGENCE")
    assert data["differentialConfidence"] is not None
    assert 0.0 <= data["differentialConfidence"] <= 1.0
    assert "id" in data
    assert "timestamp" in data


def test_predict_unified_endpoint():
    """Verify unified /api/predict entrypoint routes correctly."""
    payload = {
        "title": "Central Bank Policy",
        "text": "Central banks announced coordinated treasury actions.",
        "model": "both",
    }
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["lstm"] is not None
    assert data["bert"] is not None


def test_benchmarks_endpoint():
    """Verify empirical benchmarks endpoint returns all benchmark models."""
    response = client.get("/api/benchmarks")
    assert response.status_code == 200
    benchmarks = response.json()
    assert isinstance(benchmarks, list)
    assert len(benchmarks) >= 3

    names = [b["name"] for b in benchmarks]
    assert any("BERT" in n for n in names)
    assert any("BiLSTM" in n for n in names)
    assert any("Champion" in b["tag"] for b in benchmarks)

    champion = next(b for b in benchmarks if b["isChampion"])
    assert champion["f1Score"] > 0.8
    assert "confusionMatrix" in champion
    assert champion["confusionMatrix"]["tp"] > 0
    assert len(champion["rocCurve"]) > 0


# Edge Cases & Validation Testing
def test_predict_empty_text_error():
    """Verify 422 validation error when text is empty."""
    response = client.post("/api/predict/lstm", json={"text": ""})
    assert response.status_code == 422


def test_predict_whitespace_text_error():
    """Verify 422 validation error when text contains only whitespace."""
    response = client.post("/api/predict/bert", json={"text": "   \n\t   "})
    assert response.status_code == 422


def test_predict_missing_text_error():
    """Verify 422 validation error when text field is missing."""
    response = client.post("/api/predict/both", json={"title": "No text body"})
    assert response.status_code == 422


def test_predict_invalid_model_error():
    """Verify 422 validation error when model parameter is invalid."""
    response = client.post("/api/predict", json={"text": "Valid text", "model": "invalid-model"})
    assert response.status_code == 422


def test_predict_long_text_success():
    """Verify system handles long text inputs without errors or memory issues."""
    long_text = "The quick brown fox jumps over the lazy dog. " * 500
    response = client.post("/api/predict/lstm", json={"text": long_text})
    assert response.status_code == 200
    data = response.json()
    assert data["tokensCount"] >= 4500


def test_predict_unicode_and_emojis():
    """Verify endpoint gracefully handles unicode and emojis without encoding errors."""
    payload = {
        "title": "🚨 BREAKING NEWS 🗞️",
        "text": "Shocking secret miracle cure revealed! 💉💊😱 Special report: https://news.example.com",
        "model": "both",
    }
    response = client.post("/api/predict/both", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["targetModel"] == "both"
    assert len(data["lstm"]["saliencyTokens"]) > 0
    assert len(data["bert"]["saliencyTokens"]) > 0


def test_predict_punctuation_and_symbols():
    """Verify endpoint handles text with heavy punctuation, URLs, and symbols."""
    payload = {
        "title": "Economic Report: #1 Inflation @ 2.5% ($100B+)",
        "text": "The Federal Reserve & European Central Bank announced 25-50 bps adjustments! [Update: 100% verified].",
        "model": "both",
    }
    response = client.post("/api/predict/both", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["targetModel"] == "both"


def test_lstm_predictor_pytorch_loaded_path(monkeypatch):
    """Verify LSTMPredictor executes _predict_pytorch when is_loaded is True and TORCH_AVAILABLE is simulated."""
    from unittest.mock import MagicMock

    import backend.app.models.lstm as lstm_mod
    from backend.app.models.lstm import LSTMPredictor

    predictor = LSTMPredictor()
    mock_model = MagicMock()
    mock_tensor = MagicMock()
    mock_tensor.__getitem__.return_value.item.return_value = 0.85
    mock_model.return_value = (mock_tensor, None)

    predictor.is_loaded = True
    predictor.model = mock_model

    monkeypatch.setattr(lstm_mod, "TORCH_AVAILABLE", True)

    mock_torch = MagicMock()
    mock_torch.tensor.return_value = MagicMock()
    mock_torch.no_grad.return_value.__enter__ = MagicMock()
    mock_torch.no_grad.return_value.__exit__ = MagicMock()
    monkeypatch.setattr(lstm_mod, "torch", mock_torch)

    res = predictor.predict("Breaking news story about technology")
    assert res.modelId == "lstm"
    assert res.verdict == "FAKE"
    assert res.probabilityFake == 0.85


def test_bert_predictor_transformers_loaded_path(monkeypatch):
    """Verify BertPredictor executes _predict_transformers when is_loaded is True."""
    from unittest.mock import MagicMock

    import backend.app.models.bert as bert_mod
    from backend.app.models.bert import BertPredictor

    predictor = BertPredictor()
    mock_model = MagicMock()
    mock_tokenizer = MagicMock()
    mock_tokenizer.return_value = {"input_ids": MagicMock()}

    mock_outputs = MagicMock()
    mock_model.return_value = mock_outputs

    predictor.is_loaded = True
    predictor.model = mock_model
    predictor.tokenizer = mock_tokenizer

    monkeypatch.setattr(bert_mod, "TORCH_AVAILABLE", True)

    mock_torch = MagicMock()
    mock_torch.no_grad.return_value.__enter__ = MagicMock()
    mock_torch.no_grad.return_value.__exit__ = MagicMock()
    mock_probs = MagicMock()
    mock_probs.shape = [1, 2]
    mock_probs.__getitem__.return_value.item.return_value = 0.92
    mock_torch.softmax.return_value = mock_probs
    monkeypatch.setattr(bert_mod, "torch", mock_torch)

    res = predictor.predict("Official report from central authority")
    assert res.modelId == "bert"
    assert res.verdict == "REAL"
    assert res.probabilityReal == 0.92
