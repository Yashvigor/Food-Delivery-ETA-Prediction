import pandas as pd
import numpy as np

def map_traffic_severity(traffic_level: str) -> int:
    """Maps traffic level to severity score."""
    mapping = {
        "Low": 1,
        "Medium": 2,
        "High": 3,
        "Jam": 4
    }
    # Return 2 (Medium) as default if unexpected value is passed
    return mapping.get(str(traffic_level).strip().capitalize(), 2)

def map_weather_severity(weather_condition: str) -> int:
    """Maps weather condition to severity score."""
    mapping = {
        "Sunny": 1,
        "Cloudy": 2,
        "Rainy": 3,
        "Rain": 3,
        "Storm": 4
    }
    # Return 1 (Sunny) as default if unexpected value is passed
    return mapping.get(str(weather_condition).strip().capitalize(), 1)

def get_distance_bucket(distance: float) -> str:
    """Categorizes distance into short, medium, long, very long buckets."""
    if distance <= 3.0:
        return "Short"
    elif distance <= 8.0:
        return "Medium"
    elif distance <= 15.0:
        return "Long"
    else:
        return "Very Long"

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies feature engineering steps to the input DataFrame.
    Operates on a copy to avoid SettingWithCopy warnings.
    """
    df_feat = df.copy()

    # 1. Traffic and Weather Severity Scores
    if "Traffic_Level" in df_feat.columns:
        df_feat["Traffic_Severity_Score"] = df_feat["Traffic_Level"].apply(map_traffic_severity)
    
    if "Weather" in df_feat.columns:
        df_feat["Weather_Severity_Score"] = df_feat["Weather"].apply(map_weather_severity)

    # 2. Distance Buckets
    if "Distance_km" in df_feat.columns:
        df_feat["Distance_Bucket"] = df_feat["Distance_km"].apply(get_distance_bucket)

    # 3. Time Features
    # If the dataset already contains strings, we align them to the requested flags:
    # is_peak_hour, is_weekend, is_night (as 1 or 0 or Yes/No)
    if "Peak_Hour" in df_feat.columns:
        df_feat["is_peak_hour"] = df_feat["Peak_Hour"].apply(lambda x: 1 if str(x).lower() == "yes" else 0)
    
    if "Day_of_Week" in df_feat.columns:
        df_feat["is_weekend"] = df_feat["Day_of_Week"].apply(
            lambda x: 1 if str(x).strip().capitalize() in ["Saturday", "Sunday"] else 0
        )
        
    if "Time_of_Day" in df_feat.columns:
        df_feat["is_night"] = df_feat["Time_of_Day"].apply(
            lambda x: 1 if str(x).strip().capitalize() == "Night" else 0
        )

    return df_feat

if __name__ == "__main__":
    # Test feature engineering
    test_data = pd.DataFrame({
        "Distance_km": [2.5, 5.0, 12.0, 18.0],
        "Traffic_Level": ["Low", "Medium", "High", "Jam"],
        "Weather": ["Sunny", "Cloudy", "Rainy", "Storm"],
        "Peak_Hour": ["No", "Yes", "Yes", "No"],
        "Day_of_Week": ["Monday", "Wednesday", "Saturday", "Sunday"],
        "Time_of_Day": ["Morning", "Afternoon", "Night", "Night"]
    })
    
    engineered = engineer_features(test_data)
    print("Engineered DataFrame columns:")
    print(engineered.columns.tolist())
    print("\nSample engineered values:")
    print(engineered[["Distance_Bucket", "Traffic_Severity_Score", "Weather_Severity_Score", "is_peak_hour", "is_weekend", "is_night"]])
