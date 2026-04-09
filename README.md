# Supply Chain Intelligence & Sales Decline Analysis System

A production-quality dashboard for analyzing product sales lifecycles, detecting declines, and identifying probable causes.

## Features
- **Decline Detection**: Rule-based algorithm to flag sustained sales drops (>15% for 3+ months).
- **Cause Analysis**: Systematically checks price, rating, market trend, competitor launches, and stockouts.
- **Interactive Dashboard**: Streamlit UI with Plotly charts, 3D visualizations, and comparative analysis.

## Project Structure
```
project-root/
├── data/               # Place CSV datasets here
├── modules/            # Analysis Logic & Data Processing
│   ├── data_collection.py
│   ├── data_cleaning.py
│   ├── features.py
│   └── analysis.py
├── dashboard/
│   └── app.py          # Streamlit Entrypoint
└── tests/              # Unit tests
```

## Setup & Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Dashboard**:
   ```bash
   python -m streamlit run dashboard/app.py
   ```
   *Note: Runs locally on port 8501.*

## Methodology

### Decline Detection
The system identifies a "decline" if:
1. A peak sales month is identified (using 3-month rolling average).
2. Sales drop by **>15%** (configurable) relative to peak.
3. This drop is sustained for at least **3 consecutive months**.

### Cause Ranking
Once a decline is flagged, we compare the **3-month pre-peak** period vs. **3-month post-decline** period:
- **Price Increase**: Price rose > 5%.
- **Satisfaction Drop**: Rating fell > 5%.
- **Market Interest**: Google Trends index fell > 10%.
- **Competitor Launch**: Launch detected within ±2 months of decline start.
- **Stockouts**: Stockout rate > 10%.

## Input Data Format
Expects a CSV with columns:
- `product_id` (string)
- `date` (YYYY-MM-DD)
- `sales` (int)
- `price` (float)
- `rating` (float)
- `trend_index` (float, 0-100)
- `competitor_launch` (0/1)
- *Optional*: `category`, `stockouts`, `promo_flag`
