import matplotlib.pyplot as plt
from pathlib import Path


OUTPUT = Path(
    "results/figures"
)

OUTPUT.mkdir(
    exist_ok=True
)


fig, ax = plt.subplots(
    figsize=(8,10)
)


ax.axis("off")


boxes = [
    ("TON_IoT\nNetwork Dataset",0.5,0.9),
    ("Data Preprocessing\n& Feature Extraction",0.5,0.75),
    ("Random Forest\nIDS Classifier",0.5,0.6),
    ("Attack Probability\nPrediction",0.5,0.45),
    ("Risk Assessment\nEngine",0.5,0.3),
    ("Risk Score +\nSeverity Classification",0.5,0.15),
    ("Adaptive Response\nALLOW / ALERT / BLOCK",0.5,0.02)
]


for text,x,y in boxes:

    ax.text(
        x,
        y,
        text,
        ha="center",
        va="center",
        fontsize=12,
        bbox=dict(
            boxstyle="round",
            facecolor="white",
            edgecolor="black"
        )
    )


for i in range(len(boxes)-1):

    ax.annotate(
        "",
        xy=(0.5,boxes[i+1][2]+0.04),
        xytext=(0.5,boxes[i][2]-0.04),
        arrowprops=dict(
            arrowstyle="->"
        )
    )


plt.savefig(
    OUTPUT / "riskadaptive_architecture.png",
    dpi=300,
    bbox_inches="tight"
)


plt.close()


print(
    "Architecture figure saved"
)
