import os
import random
import numpy as np
import pandas as pd

def generate_synthetic_data(output_path="data/raw/deliveries.csv", num_records=6000, seed=42):
    """
    Generates a high-fidelity synthetic dataset for food delivery ETAs with realistic correlations.
    """
    np.random.seed(seed)
    random.seed(seed)

    # Ensure output directories exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    data = []

    for i in range(num_records):
        order_id = f"ORD{i+1:05d}"
        
        # 1. Distance (km): Skewed towards short distances (most deliveries are local)
        distance = np.random.exponential(scale=4.5) + 0.5
        distance = min(distance, 28.0)  # Cap distance at 28km
        distance = round(distance, 2)

        # 2. Weather conditions
        weather = np.random.choice(
            ["Sunny", "Cloudy", "Rainy", "Storm"], 
            p=[0.50, 0.25, 0.18, 0.07]
        )
        
        # 3. Traffic level
        traffic = np.random.choice(
            ["Low", "Medium", "High", "Jam"], 
            p=[0.30, 0.40, 0.20, 0.10]
        )

        # 4. Vehicle Type
        vehicle = np.random.choice(
            ["Cycle", "Scooter", "Bike"], 
            p=[0.15, 0.50, 0.35]
        )
        
        # 5. Courier Age and Experience
        courier_age = int(np.random.randint(18, 55))
        # Experience is correlated with age
        max_exp = max(1, courier_age - 18)
        courier_experience = int(np.random.randint(1, min(max_exp, 15) + 1))

        # 6. Restaurant Rating (1 to 5)
        restaurant_rating = round(float(np.random.uniform(3.0, 5.0)), 1)
        # Sometime raw ratings can be low
        if random.random() < 0.05:
            restaurant_rating = round(float(np.random.uniform(1.5, 3.0)), 1)

        # 7. Order Size
        order_size = np.random.choice(
            ["Small", "Medium", "Large"], 
            p=[0.30, 0.50, 0.20]
        )

        # 8. Prep Time (correlated with rating and size)
        base_prep = 15
        if order_size == "Small":
            base_prep += np.random.randint(0, 10)
        elif order_size == "Medium":
            base_prep += np.random.randint(5, 15)
        else:  # Large
            base_prep += np.random.randint(15, 30)
            
        # Low rating resturants take longer
        if restaurant_rating < 3.0:
            base_prep += np.random.randint(5, 12)
            
        # Weather delay in prep
        if weather in ["Rainy", "Storm"]:
            base_prep += np.random.randint(3, 8)
            
        prep_time = int(base_prep)

        # 9. Time features
        hour = np.random.randint(8, 23)  # Operating hours 8 AM to 11 PM
        if hour < 12:
            time_of_day = "Morning"
        elif hour < 17:
            time_of_day = "Afternoon"
        else:
            time_of_day = "Night"
            
        # Peak Hour flag (12-14 lunch, 18-21 dinner)
        is_peak_hour = "Yes" if (12 <= hour <= 14 or 18 <= hour <= 21) else "No"
        
        # Day of week
        day_of_week = np.random.choice(
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        )
        is_weekend = "Yes" if day_of_week in ["Saturday", "Sunday"] else "No"

        # 10. Special Days
        festival_day = "Yes" if random.random() < 0.08 else "No"
        holiday = "Yes" if (is_weekend == "Yes" or random.random() < 0.05) else "No"

        # 11. Customer Location Type
        location_type = np.random.choice(["Residential", "Commercial"], p=[0.65, 0.35])

        # --- PHYSICS-BASED DELIVERY TIME CALCULATION ---
        # Base Speed in km/h based on Vehicle Type
        if vehicle == "Cycle":
            base_speed = 12.0
        elif vehicle == "Scooter":
            base_speed = 22.0
        else:  # Bike
            base_speed = 28.0
            
        # Speed modifiers
        # Weather Penalty
        weather_mods = {"Sunny": 1.0, "Cloudy": 0.95, "Rainy": 0.72, "Storm": 0.50}
        weather_mod = weather_mods[weather]
        
        # Traffic Penalty
        traffic_mods = {"Low": 1.0, "Medium": 0.82, "High": 0.55, "Jam": 0.30}
        traffic_mod = traffic_mods[traffic]
        
        # Courier Experience bonus (faster routing, shortcut knowledge)
        experience_mod = 1.0 + (courier_experience * 0.02)
        experience_mod = min(experience_mod, 1.25)
        
        # Courier Age minor penalty for extreme age ranges (reflexes, stamina)
        age_mod = 1.0
        if courier_age > 48:
            age_mod = 0.92
        elif courier_age < 21:
            age_mod = 0.97
            
        # Compute dynamic travel speed
        travel_speed = base_speed * weather_mod * traffic_mod * experience_mod * age_mod
        travel_speed = max(travel_speed, 4.0)  # Courier cannot go slower than a walk (4 km/h)
        
        # Transit time in minutes
        travel_time_min = (distance / travel_speed) * 60.0

        # Location Handoff time
        handoff_time = 3.0 if location_type == "Residential" else 7.0  # Commercial offices take longer

        # Peak hours or special day delays
        special_delay = 0.0
        if is_peak_hour == "Yes":
            special_delay += np.random.uniform(2, 6)
        if festival_day == "Yes":
            special_delay += np.random.uniform(4, 10)
            
        # Combine elements
        expected_delivery_time = prep_time + travel_time_min + handoff_time + special_delay
        
        # Add random unexpected event delays (flats, elevator issues, order changes)
        noise_std = 3.0
        if traffic in ["High", "Jam"]:
            noise_std += 2.0
        if weather in ["Rainy", "Storm"]:
            noise_std += 3.0
            
        unexpected_noise = np.random.normal(loc=0.0, scale=noise_std)
        
        # Target variable (Delivery Time in Minutes)
        delivery_time = round(expected_delivery_time + unexpected_noise, 1)
        delivery_time = max(delivery_time, 12.0)  # Minimum food delivery is 12 mins
        
        data.append({
            "Order_ID": order_id,
            "Distance_km": distance,
            "Preparation_Time": prep_time,
            "Courier_Age": courier_age,
            "Courier_Experience": courier_experience,
            "Vehicle_Type": vehicle,
            "Weather": weather,
            "Traffic_Level": traffic,
            "Time_of_Day": time_of_day,
            "Day_of_Week": day_of_week,
            "Festival_Day": festival_day,
            "Holiday": holiday,
            "Restaurant_Rating": restaurant_rating,
            "Order_Size": order_size,
            "Customer_Location_Type": location_type,
            "Peak_Hour": is_peak_hour,
            "Delivery_Time_Min": delivery_time
        })

    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    print(f"Successfully generated synthetic dataset with {len(df)} records at: {output_path}")
    return df

if __name__ == "__main__":
    generate_synthetic_data()
