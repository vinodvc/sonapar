import pandas as pd
import numpy as np

def get_sku_data():
    np.random.seed(42)
    skus = [
        {"SKU": "CB-120A", "Description": "Circuit Breaker 20A",      "Category": "Electrical",   "Monthly_Hits": 420, "Avg_Units": 14, "Current_Zone": "C", "Current_Aisle": 7, "Current_Bin": 22, "Unit_Weight_lbs": 1.2},
        {"SKU": "CB-240A", "Description": "Circuit Breaker 40A",      "Category": "Electrical",   "Monthly_Hits": 390, "Avg_Units": 11, "Current_Zone": "C", "Current_Aisle": 7, "Current_Bin": 24, "Unit_Weight_lbs": 1.8},
        {"SKU": "WN-14G",  "Description": "Wire Nut 14 AWG (100pk)",  "Category": "Wiring",       "Monthly_Hits": 510, "Avg_Units": 32, "Current_Zone": "B", "Current_Aisle": 4, "Current_Bin": 12, "Unit_Weight_lbs": 0.3},
        {"SKU": "CP-15A",  "Description": "Conduit Pipe 15ft",        "Category": "Conduit",      "Monthly_Hits": 180, "Avg_Units": 6,  "Current_Zone": "A", "Current_Aisle": 1, "Current_Bin": 3,  "Unit_Weight_lbs": 8.5},
        {"SKU": "EM-LED4", "Description": "LED Panel 4ft 40W",        "Category": "Lighting",     "Monthly_Hits": 340, "Avg_Units": 9,  "Current_Zone": "B", "Current_Aisle": 5, "Current_Bin": 8,  "Unit_Weight_lbs": 2.1},
        {"SKU": "PB-100",  "Description": "Push Button Switch",       "Category": "Controls",     "Monthly_Hits": 290, "Avg_Units": 18, "Current_Zone": "B", "Current_Aisle": 4, "Current_Bin": 19, "Unit_Weight_lbs": 0.2},
        {"SKU": "TR-480",  "Description": "Transformer 480V",         "Category": "Power",        "Monthly_Hits": 65,  "Avg_Units": 2,  "Current_Zone": "A", "Current_Aisle": 1, "Current_Bin": 7,  "Unit_Weight_lbs": 42.0},
        {"SKU": "CB-EP20", "Description": "GFCI Breaker 20A",         "Category": "Electrical",   "Monthly_Hits": 455, "Avg_Units": 16, "Current_Zone": "C", "Current_Aisle": 8, "Current_Bin": 31, "Unit_Weight_lbs": 1.4},
        {"SKU": "RW-12G",  "Description": "Romex Wire 12AWG 250ft",   "Category": "Wiring",       "Monthly_Hits": 280, "Avg_Units": 8,  "Current_Zone": "B", "Current_Aisle": 3, "Current_Bin": 14, "Unit_Weight_lbs": 12.0},
        {"SKU": "JB-4SQ",  "Description": "Junction Box 4-Square",    "Category": "Enclosures",   "Monthly_Hits": 520, "Avg_Units": 25, "Current_Zone": "C", "Current_Aisle": 9, "Current_Bin": 40, "Unit_Weight_lbs": 0.5},
        {"SKU": "FL-T8",   "Description": "Fluorescent Tube T8 4ft",  "Category": "Lighting",     "Monthly_Hits": 95,  "Avg_Units": 24, "Current_Zone": "A", "Current_Aisle": 2, "Current_Bin": 5,  "Unit_Weight_lbs": 0.4},
        {"SKU": "MC-3/4",  "Description": "MC Cable 3/4in 100ft",     "Category": "Conduit",      "Monthly_Hits": 210, "Avg_Units": 5,  "Current_Zone": "B", "Current_Aisle": 6, "Current_Bin": 17, "Unit_Weight_lbs": 18.0},
        {"SKU": "DP-100A", "Description": "Distribution Panel 100A",  "Category": "Power",        "Monthly_Hits": 45,  "Avg_Units": 1,  "Current_Zone": "A", "Current_Aisle": 1, "Current_Bin": 2,  "Unit_Weight_lbs": 28.0},
        {"SKU": "OL-3PH",  "Description": "Overload Relay 3-Phase",   "Category": "Controls",     "Monthly_Hits": 155, "Avg_Units": 4,  "Current_Zone": "B", "Current_Aisle": 5, "Current_Bin": 21, "Unit_Weight_lbs": 0.9},
        {"SKU": "WT-STD",  "Description": "Wire Tie Std 100pk",       "Category": "Accessories",  "Monthly_Hits": 480, "Avg_Units": 40, "Current_Zone": "C", "Current_Aisle": 10,"Current_Bin": 38, "Unit_Weight_lbs": 0.2},
    ]
    df = pd.DataFrame(skus)
    df["Annual_Hits"] = df["Monthly_Hits"] * 12
    df["Velocity_Class"] = pd.cut(df["Monthly_Hits"], bins=[0,150,350,600], labels=["C","B","A"])
    return df


def get_opco_data():
    months = ["Oct","Nov","Dec","Jan","Feb","Mar"]
    data = {
        "Crawford Electric": {
            "Pick_Accuracy":    [97.2, 97.5, 96.8, 97.9, 98.1, 98.4],
            "OTD":              [91.0, 92.3, 89.5, 93.1, 94.0, 94.8],
            "DIP_Days":         [3.8,  3.5,  4.1,  3.2,  3.0,  2.9],
            "Excess_Inv_Pct":   [18.2, 17.5, 19.0, 16.8, 15.9, 15.1],
            "LPMH":             [82,   84,   80,   87,   89,   91],
            "Slotting_Score":   [72,   73,   71,   75,   77,   79],
        },
        "North Coast Electric": {
            "Pick_Accuracy":    [94.1, 93.8, 92.5, 94.7, 95.2, 95.8],
            "OTD":              [87.2, 86.5, 84.0, 88.3, 89.1, 90.0],
            "DIP_Days":         [5.1,  5.4,  6.2,  4.9,  4.7,  4.5],
            "Excess_Inv_Pct":   [24.5, 25.1, 27.3, 23.8, 22.9, 21.7],
            "LPMH":             [71,   69,   65,   73,   75,   76],
            "Slotting_Score":   [58,   57,   54,   61,   63,   65],
        },
        "Viking Electric": {
            "Pick_Accuracy":    [98.5, 98.7, 98.2, 98.9, 99.1, 99.3],
            "OTD":              [95.3, 95.8, 94.9, 96.2, 96.8, 97.1],
            "DIP_Days":         [2.4,  2.3,  2.6,  2.1,  2.0,  1.9],
            "Excess_Inv_Pct":   [11.3, 10.8, 12.1, 10.2, 9.8,  9.3],
            "LPMH":             [96,   98,   94,   101,  103,  105],
            "Slotting_Score":   [88,   89,   87,   91,   93,   94],
        },
    }
    return data, months


def get_roi_defaults():
    return {
        "pickers": 12,
        "hourly_wage": 22.50,
        "hours_per_shift": 8,
        "shifts_per_year": 250,
        "avg_travel_ft_per_pick": 210,
        "picks_per_hour": 55,
        "ft_per_minute": 250,
        "optimization_travel_reduction": 0.22,
    }
