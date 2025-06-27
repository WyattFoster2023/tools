import pandas as pd
from fpdf import FPDF

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
    ("Labor; Drywall removal and repair, full shower set replacement", 150.00)
]

# Create PDF
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.cell(200, 10, txt="Lowe's Parts Invoice", ln=1, align="C")
pdf.cell(200, 10, txt="", ln=1, align="C")

# Table header
pdf.set_font("Arial", 'B', 12)
pdf.cell(150, 10, "Part", border=1)
pdf.cell(40, 10, "Price ($)", border=1, ln=1)
pdf.set_font("Arial", size=12)

# Table rows
for part, price in parts:
    pdf.cell(150, 10, part, border=1)
    pdf.cell(40, 10, f"${price:.2f}", border=1, ln=1)

# Total
pdf.set_font("Arial", 'B', 12)
total = sum(price for _, price in parts)
pdf.cell(150, 10, "Total", border=1)
pdf.cell(40, 10, f"${total:.2f}", border=1, ln=1)

# Save PDF
pdf.output("Lowe's Parts Invoice.pdf")

