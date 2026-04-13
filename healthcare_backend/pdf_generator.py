import os
import matplotlib
matplotlib.use('Agg')  # Backend set for server use

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime

# Project Settings
PATIENT_NAME = "Kritisha Oberoi"

def generate_pdf_batch(readings):
    """
    Generate a PDF report for multiple readings.
    Includes patient name, timestamps, and highlights abnormal readings.
    """
    # 1. Ensure 'records' folder exists
    if not os.path.exists("records"):
        os.makedirs("records")

    timestamp_now = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"records/Health_Report_{timestamp_now}.pdf"

    print(f"[PDF BATCH] Generating PDF for {len(readings)} readings")

    try:
        with PdfPages(filename) as pdf:
            # -------------------------------------------------------
            # Page 1: Summary Table
            # -------------------------------------------------------
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.axis("off")

            # Table Header
            table_data = [["No.", "Time", "Heart Rate", "SpO2", "Status"]]
            
            # Fill Table Rows
            for i, r in enumerate(readings, 1):
                time_val = r.get('time', 'N/A')
                table_data.append([i, time_val, r['hr'], r['spo2'], r['status']])

            # Create the Table
            table = ax.table(cellText=table_data, loc='center', cellLoc='center')
            table.auto_set_font_size(False)
            table.set_fontsize(10)

            # Column widths scaling
            col_widths = [0.05, 0.25, 0.15, 0.15, 0.25]
            for j, width in enumerate(col_widths):
                for i in range(len(table_data)):
                    table[i, j].set_width(width)

            table.scale(1, 1.8)  # Vertical spacing for readability
            ax.set_title(f"Health Report - {PATIENT_NAME}", fontsize=14, pad=20)

            # Highlight abnormal readings (Red Background)
            for row_idx, r in enumerate(readings, 1):
                hr = r['hr']
                spo2 = r['spo2']
                # Thresholds: HR (60-100), SpO2 (>=95)
                if hr < 60 or hr > 100 or spo2 < 95:
                    for col_idx in range(5):
                        table[(row_idx, col_idx)].set_facecolor("#f8d7da")

            pdf.savefig(fig)
            plt.close(fig)

            # -------------------------------------------------------
            # Page 2: Visualizations (Trends)
            # -------------------------------------------------------
            hr_values = [r['hr'] for r in readings]
            spo2_values = [r['spo2'] for r in readings]
            timestamps = [r.get('time', '').split(' ')[-1] if ' ' in r.get('time', '') else 'N/A' for r in readings]
            indices = list(range(1, len(readings) + 1))

            fig, ax = plt.subplots(figsize=(10, 5))
            
            # Plot Heart Rate and SpO2
            ax.plot(indices, hr_values, marker='o', label='Heart Rate (BPM)', color='#1f77b4', linewidth=2)
            ax.plot(indices, spo2_values, marker='s', label='SpO2 (%)', color='#2ca02c', linewidth=2)

            # Mark abnormal points with Red dots/crosses
            for i, r in enumerate(readings):
                if r['hr'] < 60 or r['hr'] > 100:
                    ax.plot(i+1, r['hr'], 'ro')
                if r['spo2'] < 95:
                    ax.plot(i+1, r['spo2'], 'rx', markersize=10)

            ax.set_xticks(indices)
            ax.set_xticklabels(timestamps, rotation=45, ha='right')
            ax.set_xlabel("Time (HH:MM:SS)")
            ax.set_ylabel("Value")
            ax.set_title(f"Vitals Over Time - {PATIENT_NAME}")
            ax.legend()
            ax.grid(True, linestyle='--', alpha=0.7)
            
            plt.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)

        print(f"[PDF BATCH] Successfully Generated: {filename}")
        return filename

    except Exception as e:
        print(f"[ERROR] PDF Generation failed: {e}")
        return None