import pandas as pd

# Parts and prices extracted from all images manually
parts = [
    ("RELIABILT 1/2-in x 3-in Black Nipple", 2.70),
    ("SharkBite Max 1/2-in Push-to-Connect x 1/2-in FNPT Female Adapter", 8.26),
    ("Streamline 1/2-in x 5-ft Copper Type L Pipe", 17.97),
    ("SharkBite Max 1/2-in Push-to-Connect x 1/2-in FNPT 90-Degree Drop Ear Elbow", 10.15),
    ("SharkBite Max 1/2-in Push-to-Connect x 1/2-in FNPT Female Adapter (Qty: 2)", 16.52),
    ("Bernzomatic Soldering Propane Torch kit 14.1-oz", 21.58),
    ("Moen Adler Bathtub and Shower Faucet", 98.00),
    ("SHEETROCK Composite Drywall Repair Patch", 6.82),
    ("SHEETROCK Premixed Drywall Joint Compound", 5.29),
    ("Kobalt 7/8-in Copper Tube Cutter", 12.85),
    ("Streamline SWT x SWT Drop Ear Elbow", 16.08),
    ("Streamline 1/2-in x 5-ft Copper Type L Pipe", 17.97),
    ("RectorSeal Nokorode Soldering Flux", 3.85),
    ("Streamline SWT x FIP Drop Ear Elbow", 12.06),
    ("Harris Lead-Free Plumbing Solder", 24.28),
]

# Create DataFrame
df = pd.DataFrame(parts, columns=["Item", "Price"])

# Calculate subtotal
subtotal = df["Price"].sum()

# Add labor
labor_description = "Labor; Drywall removal and repair, full shower set replacement"
labor_cost = 150.00

# Create final invoice DataFrame
invoice_df = df.append({"Item": labor_description, "Price": labor_cost}, ignore_index=True)
invoice_df.loc["Total"] = ["Total", invoice_df["Price"].sum()]

import ace_tools as tools; tools.display_dataframe_to_user(name="Lowe's Parts Invoice", dataframe=invoice_df)
