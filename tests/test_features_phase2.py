from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.features.embeddings import average_word2vec, build_embedding_matrix, train_word2vec
from src.features.preprocessing import (
    MissingIndicatorTransformer,
    SmoothedTargetEncoder,
    build_numeric_pipeline,
    build_preprocessor,
)
from src.features.text import TextNormalizer, TextStatisticsTransformer, TfidfTextPipeline
from src.features.unsupervised_features import UnsupervisedFeatureAugmenter
from src.models.unsupervised import UnsupervisedAnalyzer, reduce_for_visualization


def numeric_fixture() -> tuple[pd.DataFrame, np.ndarray]:
    frame = pd.DataFrame(
        {
            "length": [1.0, 2.0, np.nan, 4.0, 5.0, 6.0, 7.0, np.nan],
            "source": ["a", "b", "a", "c", "b", "c", "a", "b"],
        }
    )
    labels = np.asarray([0, 1, 0, 1, 0, 1, 0, 1])
    return frame, labels


def cluster_fixture() -> np.ndarray:
    return np.asarray(
        [[0.0, 0.0], [0.1, 0.1], [0.2, 0.0], [5.0, 5.0], [5.1, 5.0], [5.0, 5.2], [10.0, 10.0], [10.1, 10.0]],
        dtype=np.float32,
    )


def test_text_statistics_and_normalization_schema():
    normalizer = TextNormalizer(stop_words="english", stemming=False, lemmatization=False).fit(["A test"])
    transformed = normalizer.transform(["The QUICK test!"])
    assert transformed.tolist() == ["quick test"]
    stats = TextStatisticsTransformer().fit(["A short sentence."])
    output = stats.transform(["A short sentence."])
    assert list(output.columns) == list(TextStatisticsTransformer.feature_names)
    assert output.shape == (1, len(TextStatisticsTransformer.feature_names))


def test_tfidf_fit_only_on_train_and_validation_mutation_does_not_change_vocabulary():
    train = ["real report verified", "fake claim fabricated", "real report published", "fake claim repeated"]
    validation = ["unseen validation phrase"]
    pipeline = TfidfTextPipeline(min_df=1, max_df=1.0).fit(train)
    names_before = pipeline.get_feature_names().copy()
    pipeline.transform(["changed validation phrase"])
    assert np.array_equal(names_before, pipeline.get_feature_names())
    assert pipeline.transform(validation).shape[1] == len(names_before)


def test_preprocessing_imputation_encoding_scaling_and_leakage():
    train, labels = numeric_fixture()
    validation = train.iloc[:2].copy()
    validation.loc[:, "length"] = [1000.0, 2000.0]
    preprocessor = build_preprocessor(["length"], ["source"], imputation="median", scaling="standard")
    train_output = preprocessor.fit_transform(train, labels)
    validation_output = preprocessor.transform(validation)
    assert train_output.shape[1] == validation_output.shape[1]
    median_before = preprocessor.named_transformers_["numeric"].named_steps["imputer"].statistics_.copy()
    preprocessor.transform(validation.assign(length=[-1000.0, -2000.0]))
    assert np.array_equal(median_before, preprocessor.named_transformers_["numeric"].named_steps["imputer"].statistics_)

    for strategy in ("mean", "median", "knn", "iterative"):
        transformed = build_numeric_pipeline(strategy, scaling="minmax").fit_transform(train[["length"]])
        assert transformed.shape[0] == len(train)
    indicators = MissingIndicatorTransformer().fit(train[["length"]]).transform(train[["length"]])
    assert indicators.shape[0] == len(train)


def test_target_encoding_is_out_of_fold_and_stable_on_held_out_rows():
    train, labels = numeric_fixture()
    encoder = SmoothedTargetEncoder(columns=["source"], n_splits=4, smoothing=2.0, random_state=42)
    train_encoded = encoder.fit_transform(train[["source"]], labels)
    validation_encoded = encoder.transform(pd.DataFrame({"source": ["unseen", "a"]}))
    assert train_encoded.shape == (len(train), 1)
    assert validation_encoded.shape == (2, 1)
    maps_before = {key: value.copy() for key, value in encoder.maps_.items()}
    encoder.transform(pd.DataFrame({"source": ["new-category"]}))
    assert encoder.maps_ == maps_before


def test_embedding_matrix_and_optional_word2vec_contract():
    vectors = {"real": np.asarray([1.0, 2.0], dtype=np.float32)}
    matrix = build_embedding_matrix({"real": 1, "missing": 2}, vectors, dimension=2)
    assert matrix.shape == (3, 2)
    assert np.array_equal(matrix[1], vectors["real"])
    pytest.importorskip("gensim")
    model = train_word2vec(["real report", "fake claim"], vector_size=4, min_count=1, epochs=2, seed=42)
    averaged = average_word2vec(["real report", "unknown token"], model)
    assert averaged.shape == (2, 4)


def test_unsupervised_models_dimensions_and_determinism():
    X = cluster_fixture()
    analyzer = UnsupervisedAnalyzer(random_state=42)
    diagnostics = analyzer.kmeans_diagnostics(X, [2, 3, 20])
    assert len(diagnostics.inertias) == 3
    analyzer.fit_kmeans(X, n_clusters=2).fit_minibatch_kmeans(X, n_clusters=2, batch_size=4)
    for linkage in ("single", "complete", "average", "ward"):
        UnsupervisedAnalyzer(random_state=42).fit_hierarchical(X, n_clusters=2, linkage=linkage)
    analyzer.fit_dbscan(X, eps=0.5, min_samples=2).fit_isolation_forest(X)
    assert analyzer.dbscan_predict(X[:2]).shape == (2,)
    assert analyzer.anomaly_scores(X).shape == (len(X),)
    assert analyzer.anomaly_labels(X).shape == (len(X),)
    pca = analyzer.fit_pca(X, n_components=2, standardize=True)
    assert pca.shape == (len(X), 2)
    assert analyzer.explained_variance_ratio_.shape == (2,)
    assert reduce_for_visualization(X, method="pca", n_components=2).shape == (len(X), 2)
    assert reduce_for_visualization(X, method="tsne", n_components=2, perplexity=2).shape == (len(X), 2)


def test_unsupervised_augmenter_fit_train_transform_held_out_schema():
    X = cluster_fixture()
    held_out = X + 100.0
    augmenter = UnsupervisedFeatureAugmenter(
        n_clusters=2,
        dbscan_eps=0.5,
        dbscan_min_samples=2,
        include_minibatch_kmeans=True,
        include_dbscan=True,
        include_anomaly=True,
    )
    with pytest.raises(RuntimeError):
        augmenter.transform(held_out)
    train_output = augmenter.fit_transform(X)
    held_out_output = augmenter.transform(held_out)
    assert train_output.shape == held_out_output.shape
    assert train_output.shape[1] == X.shape[1] + 4
    assert len(augmenter.get_feature_names_out()) == train_output.shape[1]
    with pytest.raises(ValueError, match="Input feature dimension"):
        augmenter.transform(np.column_stack([held_out, np.zeros(len(held_out))]))
