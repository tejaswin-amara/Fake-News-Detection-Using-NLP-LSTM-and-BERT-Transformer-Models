# GitHub SEO and Discoverability Execution Blueprint

## Purpose and safety boundary

This guide contains **manual GitHub UI steps** for improving repository discovery. It does not rename the repository, change its public metadata, create a social-preview image, add topics, create releases, or submit to any third-party list. Those actions remain owner-controlled. The repository remains a pattern-classification system, not an autonomous fact-checking or web-search service.

## 1. Metadata

### Recommended GitHub description

Use this exact description; it is **160 characters**, including spaces and punctuation.

> Reproducible fake-news text classification with NLP, BiLSTM, BERT, DVC, MLflow, FastAPI, ONNX, monitoring, Kubernetes, and CI/CD quality gates for research use.

To apply it, open the repository home page, select **Settings**, open **General**, update the **Description** field, and save. Confirm that the wording appears in the repository’s About section and does not wrap into an unsupported claim.

### Recommended repository name

The most concise future canonical name is **`fake-news-detection-mlops`**. Do **not** rename the existing repository during ordinary metadata work. Its current URL is referenced by citations, badges, source registers, documentation, CI history, user workflows, and the companion project context.

If a rename is separately approved, first inventory all absolute GitHub URLs, update citation metadata and source-register references, validate badge links, notify collaborators, retain GitHub’s redirect behavior, and confirm that any connected deployment or dashboard documentation still points to the intended project.

## 2. Topics

GitHub supports at most 20 public repository topics and requires lowercase letters, numbers, and hyphens [1]. Add **exactly** the following 20 topics:

```text
fake-news-detection
fake-news
misinformation-detection
natural-language-processing
nlp
machine-learning
deep-learning
text-classification
bert
transformers
lstm
pytorch
scikit-learn
fastapi
mlops
dvc
mlflow
onnx
kubernetes
github-actions
```

From the repository home page, select the settings icon next to **About**, type each topic under **Topics**, choose an existing matching topic where offered, then select **Save changes**. Recheck the resulting topics for exact spelling and remove any accidental duplicate or unsupported synonym. Do not add claims such as `fact-checking` or `web-search`, because the repository does not implement those capabilities.

## 3. Social Preview

GitHub recommends a 1280×640 px image for the best social-preview rendering and accepts PNG, JPG, or GIF files smaller than 1 MB [2]. Create a single high-contrast card with a restrained data-flow visual and the following hierarchy.

| Element | Specification |
|---|---|
| Primary title | “Fake News Detection — NLP, BiLSTM & BERT” in large, readable type. |
| Supporting line | “Reproducible text classification with DVC, MLflow, FastAPI, ONNX, and CI/CD.” |
| Safety line | “Pattern classification; not independent fact verification.” |
| Visual system | A clean text-to-model-to-monitoring flow or abstract token/network motif; use solid or carefully tested high-contrast background. |
| Safe margin | Keep critical content away from the outer 64 px on all edges to protect against crop and thumbnail loss. |
| Prohibited content | Raw article data, publisher material, personal information, credentials, non-reproducible benchmark scores, logos without permitted use, or language implying the project searches the web. |

Before upload, inspect the card at thumbnail scale and in light/dark surroundings. To apply it, open the repository **Settings**, locate **Social preview**, select **Edit**, then upload the optimized image [2]. GitHub supports transparency, but a solid background is safer when the result has not been tested on multiple social platforms [2].

## 4. Backlinking and directory submissions

Prepare a short, human-written repository summary, a clear license statement, the current README, architecture and security pages, source-provenance disclosure, and a statement of the classification limitation before proposing any listing. Never mass-submit, use generated endorsements, pay for links, or imply a relationship with a curator.

| Destination | Fit and current review expectation | Manual next action |
|---|---|---|
| [Awesome Fake News Detection](https://github.com/wangbing1416/Awesome-Fake-News-Detection) | Primarily a curated research-paper list. It invites additions through maintainer contact rather than presenting a standard software-entry workflow. | Review whether a maintained scholarly resource, dataset release note, or reproducibility evidence genuinely fits. If so, make a concise, human-reviewed inquiry; otherwise do not submit a generic project link. |
| [Awesome Machine Learning](https://github.com/josephmisiti/awesome-machine-learning) | Curates ML frameworks, libraries, and software. Its current policy requires a human-confirmation contact step before a pull request. | Submit only if the project meets its scope and originality threshold. Follow the maintainer’s current human-authorship rule; do not automate or impersonate a contributor. |
| [Awesome MLOps](https://github.com/kelvins/awesome-mlops) | Curates MLOps tools and has a contribution path. This repository’s DVC, MLflow, FastAPI, ONNX, Kubernetes, and CI assets may be relevant only if the full stack merits curation. | Read the current contribution rules, select the narrowest correct category, and propose an accurate entry without performance inflation. |
| [Best-of ML Python](https://github.com/lukasmasuch/best-of-ml-python) | A ranked Python ML list with `CONTRIBUTING.md` and structured project data. Inclusion follows its eligibility and data-quality process. | Read its current contribution and `projects.yaml` requirements; create a manual proposal only if the project qualifies as a maintained Python ML project rather than merely an application repository. |
| [GitHub topic discovery](https://github.com/topics/) | Topic pages index repositories that administrators classify with public topics. | Complete the topic step above, then inspect the topic page to verify correct categorization and comparable project terminology. |

Reconfirm the upstream contribution policy immediately before each submission because directory rules and maintainer preferences can change. Acceptance is controlled by each curator and is not guaranteed.

## References

[1] [GitHub Docs — Classifying your repository with topics](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/classifying-your-repository-with-topics)

[2] [GitHub Docs — Customizing your repository’s social media preview](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/customizing-your-repositorys-social-media-preview)
