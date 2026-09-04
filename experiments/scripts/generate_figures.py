import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


INPUT = "results/riskadaptive_output.csv"

OUTPUT = Path("results/figures")

OUTPUT.mkdir(
    exist_ok=True
)


df = pd.read_csv(INPUT)


print("Generating figures")


# Risk score distribution

plt.figure(
    figsize=(8,5)
)

plt.hist(
    df["risk_score"],
    bins=30
)

plt.xlabel(
    "Risk Score"
)

plt.ylabel(
    "Number of Samples"
)

plt.title(
    "Risk Score Distribution"
)

plt.savefig(
    OUTPUT / "risk_score_distribution.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()



# Severity distribution

severity_counts = (
    df["severity"]
    .value_counts()
)


plt.figure(
    figsize=(6,4)
)

severity_counts.plot(
    kind="bar"
)

plt.xlabel(
    "Severity Level"
)

plt.ylabel(
    "Samples"
)

plt.title(
    "Risk Severity Distribution"
)

plt.savefig(
    OUTPUT / "severity_distribution.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()



# Attack type risk average

attack_risk = (
    df.groupby("attack_type")
    ["risk_score"]
    .mean()
    .sort_values()
)


plt.figure(
    figsize=(8,5)
)

attack_risk.plot(
    kind="barh"
)

plt.xlabel(
    "Average Risk Score"
)

plt.ylabel(
    "Attack Type"
)

plt.title(
    "Average Risk Score by Attack Type"
)

plt.savefig(
    OUTPUT / "attack_risk_distribution.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()



print("Figures saved in:", OUTPUT)
