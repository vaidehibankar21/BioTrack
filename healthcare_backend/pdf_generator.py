import os
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime

PATIENT_NAME = "Kritisha Oberoi"

def generate_pdf_batch(readings):
    # Match the directory with app.py
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    RECORDS_DIR = os.path.join(BASE_DIR, 'records')
    
    if not os.path.exists(RECORDS_DIR):
        os.makedirs(RECORDS_DIR)

    timestamp_now = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(RECORDS_DIR, f"Health_Report_{timestamp_now}.pdf")

    print(f"[PDF BATCH] Generating PDF: {filename}")

    try:
        with PdfPages(filename) as pdf:
            # --- Page 1: Table ---
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.axis("off")
            table_data = [["No.", "Time", "Heart Rate", "SpO2", "Status"]]
            for i, r in enumerate(readings, 1):
                table_data.append([i, r.get('time', 'N/A'), r['hr'], r['spo2'], r['status']])

            table = ax.table(cellText=table_data, loc='center', cellLoc='center')
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            col_widths = [0.05, 0.20, 0.15, 0.15, 0.45]
            for j, width in enumerate(col_widths):
                for i in range(len(table_data)):
                    table[i, j].set_width(width)
            table.scale(1, 1.8)
            ax.set_title(f"Health Report - {PATIENT_NAME}", fontsize=14, pad=20)

            for row_idx, r in enumerate(readings, 1):
                if "Abnormal" in str(r.get('status', '')):
                    for col_idx in range(5):
                        table[(row_idx, col_idx)].set_facecolor("#f8d7da")

            pdf.savefig(fig)
            plt.close(fig)

            # --- Page 2: Graphs ---
            hr_values = [r['hr'] for r in readings]
            spo2_values = [r['spo2'] for r in readings]
            indices = list(range(1, len(readings) + 1))
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(indices, hr_values, marker='o', label='HR', color='#1f77b4')
            ax.plot(indices, spo2_values, marker='s', label='SpO2', color='#2ca02c')
            ax.set_title(f"Vitals Over Time - {PATIENT_NAME}")
            ax.legend()
            plt.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)

        return filename
    except Exception as e:
        print(f"[ERROR] PDF Generation failed: {e}")
        return None
