# Leaf Recognition Module (`leaf/`)

**Grow AI — Plant Health Classification Subsystem**  
Author: S7  
Last Updated: 2025-06-13

---

## Module Overview

This module implements a leaf health classification pipeline using **ResNet18 + pseudo-labeled Reddit images**, supporting real-time inference via `/leaf_scan` API in the Grow AI system.

It detects whether a leaf is **healthy** or **wilted**, and returns structured scoring + suggestions.

Training data sources include:
- Public indoor plant datasets
- Curated Reddit images (pseudo-labeled with model confidence)

---

## Architecture Diagram

The updated architecture integrates visual classification, health scoring, and smart watering recommendation using real-time weather forecast:

![Leaf Classifier Architecture](leaf_classifier_architecture.png)


---

## Folder Contents

| File / Folder                             | Description |
|-------------------------------------------|-------------|
| `leaf_dataset/`                           | Final training set (incl. pseudo-labeled Reddit images) |
| `leaf_cleaned_ai/`                        | Clean Reddit images used in inference |
| `leaf_classifier_final.pth`               | Model trained on public dataset only |
| `leaf_classifier_final_augmented.pth`     | Final model with Reddit pseudo-labeled images |
| `train_leaf_classifier.py`                | Baseline training script |
| `train_leaf_classifier_final_augmented.py`| Script with augmented dataset |
| `predict_leaf.py`                         | Inference function |
| `reddit_predictions.json`                 | All model predictions |
| `reddit_pseudo_labeled.json`              | Confidence ≥ 0.95 for pseudo-labeling |
| `reddit_low_confidence.json`              | Confidence ≤ 0.7 |
| `augment_dataset_with_pseudo_labels.py`   | Copy Reddit images to dataset |
| `split_reddit_by_confidence.py`           | Split predictions into high/low groups |
| `filter_and_rename.py`                    | Utility: clean image files |
| `Manually_screen_rename.py`               | Manual rename/validate helper |
| `reddit_leaf_selenium_scraper.py`         | Reddit crawler |

---

## Model Summary

- **Architecture**: ResNet18 (ImageNet pretrained)
- **Classes**: `healthy`, `wilted`
- **Input**: Leaf image (JPG, 224×224)
- **Output**: `label`, `confidence`  
- **Final Accuracy**: **84.08%** on manually labeled Reddit test set  
- **Training Dataset Size**: Kaggle + 16 Reddit high-confidence samples

---

## Usage

Train the final model:

```bash
python train_leaf_classifier_final_augmented.py

```
Run prediction on a single image:

```bash
python predict_leaf.py
```
Run batch inference on Reddit images:

```bash
python batch_predict_reddit.py
```
Split predictions by confidence:

```bash
python split_reddit_by_confidence.py
```

---

## Pseudo-Labeling Strategy

To enhance model performance, high-confidence predictions (confidence ≥ 0.95) from Reddit images were used as pseudo-labels:

- `split_reddit_by_confidence.py`:  
  Splits `reddit_predictions.json` into:
  - `reddit_pseudo_labeled.json` (for training augmentation)
  - `reddit_low_confidence.json` (for testing / inspection)

- `augment_dataset_with_pseudo_labels.py`:  
  Copies pseudo-labeled images into `leaf_dataset/` to be used in `train_leaf_classifier_final_augmented.py`
---

## Dataset Sources

1. **Kaggle Houseplant Dataset**  
   - Source: [Russell Chan on Kaggle](https://www.kaggle.com/datasets/russellchan/healthy-and-wilted-houseplant-images)  
   - Labeled images of healthy and wilted houseplants. Used under standard Kaggle open license.

2. **Reddit – r/plantclinic**  
   - Crawled by **S7** using `reddit_leaf_selenium_scraper.py`  
   - Images collected from public posts. 
   - Only high-confidence samples used for pseudo-labeling and testing.  

---

 ## Evaluation (Implemented)

The script `evaluate_leaf_model.py` compares predictions from `reddit_predictions.json` against manually validated samples (`reddit_manual_labels_template.json`), and generates:

- Accuracy / Precision / Recall / F1 Score
- Confusion matrix: `confusion_matrix_leaf.png`

Example result:
![Confusion Matrix](confusion_matrix_leaf.png)
This will provide:
- Accuracy / Precision / Recall / F1 Score
- Confusion matrix visualization
---

## Health Scoring Subsystem (`leaf/scoring/`)

This subsystem combines image feature deductions with environmental factors to produce a health_score.These scores are used in the /leaf/scan API to return personalized health insights and watering recommendations, and further exposed via /leaf/next_watering/{user_id} for front-end displa

### Key Components

| Module              | Purpose                                             |
|---------------------|-----------------------------------------------------|
| `feature_score.py`  | Deductions based on color & shape features          |
| `env_bonus.py`      | Bonus/penalty based on light and soil conditions    |
| `health_score.py`   | Combines both to produce the final health score     |

---

### Health Score Logic

#### 1. Image Feature Deductions

We deduct points from a full score of 1.0 based on visual traits:    
| Leaf Feature           | Deduction | Explanation                             |
| ---------------------- | --------- | --------------------------------------- |
| Yellowing on Leaves    | -0.35     | Chlorosis or nutrient stress            |
| Brown Patches or Edges | -0.25     | Burn marks from overexposure or dryness |
| Dark or Black Spots    | -0.20     | Possible fungal or bacterial infection  |
| Leaf Shape Deformity   | -0.15     | Warping or curling due to stress        |
| Visible Holes in Leaf  | -0.10     | Insect damage or mechanical trauma      |

<img src="./scoring/leaf_score_deduction_chart.png" width="500">

---

#### 2. Environment Score Adjustments

The environment bonus ranges from `-10` to `+10`:

- Light Level
- Soil Moisture

Each parameter contributes up to `±5` points.

<img src="./scoring/env_bonus_logic_tree.png" width="500">

---

#### 3. Combined Output

The final health score combines image and environment components and outputs a structured result:

```json
{
  "health_score": 71,
  "label": "Mild Wilt",
  "components": {
    "image_score": 61,
    "env_bonus": 10
  },
  "explanation": [
    "Light level is optimal.",
    "Soil moisture is ideal."
  ],
  "recommendations": [
    "Too much light. Consider moving to a shaded area.",
    "Soil is too dry. Watering is recommended.",
    "Visual signs of mild stress detected. Monitor leaf color and shape."
  ]
}

```

---
### Weather-Aware Watering Recommendation

We use the Open-Meteo API to check for near-future rainfall based on the user's geolocation.
This ensures watering is skipped when rain is expected — useful even for semi-outdoor environments like balconies or window sills.
---
Dataset not included in this repository due to size and licensing.  
Please follow instructions in `leaf/README.md` to rebuild the dataset locally.

---

## Smart Watering Prediction Module (`leaf/watering_model.py`)

This module predicts the optimal interval between watering based on plant and environmental features. It enhances `/leaf/next_watering/{user_id}` and `/leaf/scan` recommendations.

### Input Features
- Plant type (encoded)
- Likes bright light (boolean)
- Needs frequent water (boolean)
- Light intensity (lux)
- Soil moisture (%)

### Model Info
- **Model**: RandomForestRegressor
- **Training data**: `external_data_cleaned.csv` (n=220)
- **Output**: Recommended `water_days` (integer)

Model file: `watering_model.pkl`
Training script: `train_model.py`
Inference script: `watering_model.py`

## References
1. Shuncy. (n.d.). *What should soil moisture content be for house plants?* Retrieved from https://shuncy.com/article/what-should-soil-moisture-contenet-be-for-house-plants
2. Wikipedia contributors. (2024). *Houseplant*. Wikipedia. https://en.wikipedia.org/wiki/Houseplant
