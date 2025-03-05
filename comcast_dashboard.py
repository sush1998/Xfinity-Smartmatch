import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
import plotly.express as px

# Load Predictions and True Values
predictions_file = "predictions.json"
true_values_file = "true_values.json"

# Load Data
pred_df = pd.read_json(predictions_file)
true_df = pd.read_json(true_values_file)

# Extract Predictions from Nested JSON Structure
parsed_predictions = []
for row in pred_df[0]:
    if isinstance(row, str):  # Check if it's a string that needs parsing
        try:
            parsed_json = json.loads(row)  # Parse the JSON structure
            if isinstance(parsed_json, list):
                parsed_predictions.extend([entry["name"] for entry in parsed_json if "name" in entry])
        except json.JSONDecodeError:
            continue
    elif isinstance(row, list):  # If already a list, extract names
        parsed_predictions.extend([entry["name"] for entry in row if "name" in entry])

# Convert to DataFrame
predicted_names = pd.Series(parsed_predictions, name="Predicted")
true_names = pd.Series(true_df[0].values, name="True")

# Align lengths
min_length = min(len(predicted_names), len(true_names))
predicted_names = predicted_names[:min_length]
true_names = true_names[:min_length]

# Create Comparison DataFrame
comparison_df = pd.DataFrame({"Predicted": predicted_names, "True": true_names})

# Compute Accuracy
comparison_df["Correct"] = comparison_df["Predicted"] == comparison_df["True"]
accuracy = comparison_df["Correct"].mean() * 100

# Sankey Data Preparation
sankey_data = comparison_df.groupby(["Predicted", "True"]).size().reset_index(name="Count")

# Create Unique Label Mapping
source_labels = list(sankey_data["Predicted"].unique()) + list(sankey_data["True"].unique())
source_labels = list(dict.fromkeys(source_labels))  # Remove duplicates

# Map Labels to Index
source_map = {label: idx for idx, label in enumerate(source_labels)}
sankey_data["Source"] = sankey_data["Predicted"].map(source_map)
sankey_data["Target"] = sankey_data["True"].map(source_map)

# Create Streamlit Dashboard
st.title("Comcast Recommendation System Dashboard")

# Display Accuracy
st.metric("Prediction Accuracy", f"{accuracy:.2f}%")

# Sankey Diagram
sankey_fig = go.Figure(go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=source_labels,
    ),
    link=dict(
        source=sankey_data["Source"],
        target=sankey_data["Target"],
        value=sankey_data["Count"],
    )
))

sankey_fig.update_layout(title_text="Sankey Diagram: Predictions vs. True Values", font_size=10)
st.plotly_chart(sankey_fig)

# Display Comparison Table
st.write("Comparison of Predictions vs. True Values")
st.dataframe(comparison_df)