# SolarEnergy_Prediction

A machine learning project aimed at predicting solar energy output based on various environmental factors.

## Key Features:
      - **Real-time Weather Data**: Fetches METAR and TAF data to incorporate dynamic environmental conditions.
      - **Machine Learning Predictions**: Uses an optimized XGBoost model for accurate solar power forecasts.
      - **Cloud Coverage Integration**: Accounts for low, mid, and high-level clouds affecting solar radiation.
      - **Solar Position Calculations**: Computes solar elevation and azimuth angles for better prediction accuracy.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Hangman25/SolarEnergy_Prediction.git
   cd SolarEnergy_Prediction
   ```

2. **Set Up a Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Prepare the Data**:
   - Ensure your dataset is in the `data/` directory.
   - Update the data preprocessing scripts as needed to accommodate your data format.

2. **Train the Model**:
   ```bash
   python train_model.py
   ```

3. **Make Predictions**:
   ```bash
   python predict.py --input your_input_data.csv --output predictions.csv
   ```

## Project Structure

```
SolarEnergy_Prediction/
│── data/                # Raw and processed datasets
│   ├── raw/             # Raw data files
│   ├── processed/       # Cleaned and transformed data
│   └── metadata/        # Data description and sources
│── models/              # Saved trained models
│   ├── checkpoints/     # Model checkpoints during training
│   ├── final/           # Final trained models
│   └── logs/            # Training logs and metrics
│── scripts/             # Python scripts for training & prediction
│   ├── preprocessing.py # Data preprocessing script
│   ├── train_model.py   # Model training script
│   ├── predict.py       # Prediction script
│   └── evaluation.py    # Model evaluation script
│── docs/                # Documentation files
│   ├── README.md        # Documentation for the project
│   ├── API_guide.md     # API documentation (if applicable)
│   └── model_explanation.md # Details on model selection and performance
│── requirements.txt     # Dependencies
│── train_model.py       # Entry point for training
│── predict.py           # Entry point for predictions
│── LICENSE              # License information
│── .gitignore           # Files to be ignored by Git
```

## Tech Stack

- **Programming Language**: Python
- **Libraries**: pandas, scikit-learn, numpy, matplotlib

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your proposed changes.

## License

This project is licensed under the MIT License.

## Contact

For questions or collaboration opportunities, please reach out via the repository's issue tracker.



