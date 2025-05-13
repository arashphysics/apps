import streamlit as st
import numpy as np
import pandas as pd
import dataframe_image as dfi
from PIL import Image

st.set_page_config(page_title="Lab Schedule Generator", layout="wide")
st.title("🔬 Flexible Lab Schedule Generator")

# ----------------- Inputs ------------------
st.subheader("📥 Input Parameters")

students_input = st.text_area(
    "Enter student names (one per line):",
    "Student1\nStudent2\nStudent3"
)

dates_input = st.text_area(
    "Enter experiment dates (one per line):",
    "May 21\nMay 28\nJune 4\nJune 11\nJune 18\nJune 25\nJuly 9\nJuly 16\nJuly 23"
)

weeks_input = st.text_input(
    "Enter week numbers (comma separated):",
    "1,2,3,4,5,6,7,8,9"
)

expt_input = st.text_area(
    "Enter experiment names (one per line):",
    "expt 32\nexpt 33\nexpt 34"
)

min_gap = st.slider("Minimum spacing (gap in weeks) between experiments for each student:", 1, 5, 1)

# Process inputs
names = [name.strip() for name in students_input.strip().split("\n") if name.strip()]
dates = [d.strip() for d in dates_input.strip().split("\n") if d.strip()]
week = [int(w.strip()) for w in weeks_input.strip().split(",") if w.strip()]
expt = [e.strip() for e in expt_input.strip().split("\n") if e.strip()]

# ----------------- Run Generator ------------------
if st.button("Generate Schedule"):

    max_retries = 1000
    success = False

    for attempt in range(max_retries):
        schedule = pd.DataFrame(index=expt, columns=week)
        students_sch = pd.DataFrame(index=names, columns=expt)
        sch_arr = np.zeros((len(expt), len(week)))
        success = True

        for student in names:
            assigned_expt = np.zeros(len(expt))
            avai_expt, avai_week = np.where(sch_arr < 3)
            sorted_inds = np.argsort(avai_week)
            avai_expt = avai_expt[sorted_inds]
            avai_week = avai_week[sorted_inds]

            week_temp = np.full(len(expt), np.nan)
            week_index = 0
            retry_count = 0

            while (assigned_expt == 0).any():
                retry_count += 1
                if retry_count > 1000:
                    success = False
                    break

                exp_need = np.random.choice(np.where(assigned_expt == 0)[0])
                week_for_expt = avai_week[avai_expt == exp_need]

                if len(week_for_expt) == 0:
                    success = False
                    break

                if week_index == 0:
                    wk = week_for_expt[0]
                else:
                    valid_weeks = sorted([
                        w for w in week_for_expt
                        if all(np.abs(w - week_temp[:week_index]) > min_gap)
                    ])
                    if len(valid_weeks) == 0:
                        continue
                    wk = valid_weeks[0]

                week_temp[week_index] = wk
                assigned_expt[exp_need] = 1
                week_index += 1

                date_label = dates[wk] if wk < len(dates) else f"Week {wk+1}"
                students_sch.loc[student, expt[exp_need]] = f"Week {wk + 1}, {date_label}"
                sch_arr[exp_need, wk] += 1

                if pd.isna(schedule.iloc[exp_need, wk]):
                    schedule.iloc[exp_need, wk] = student
                else:
                    schedule.iloc[exp_need, wk] += ', ' + student

            if not success:
                break

        if success:
            break

    # ----------------- Display Output ------------------
    if success:
        st.success(f"✅ Schedule completed after {attempt + 1} attempt(s).")
        col_labels = [f"Week {i + 1}, {dates[i]}" if i < len(dates) else f"Week {i + 1}" for i in range(len(week))]
        schedule.columns = col_labels

        # Save and show images
        schedule_img_path = "full_schedule.png"
        students_img_path = "students_schedule.png"

        try:
            dfi.export(schedule.transpose(), schedule_img_path, dpi=300, table_conversion='matplotlib')
            dfi.export(students_sch, students_img_path, dpi=300, table_conversion='matplotlib')


            st.subheader("🖼️ Full Schedule (by Experiment)")
            st.image(Image.open(schedule_img_path), caption="Full Schedule by Experiment", use_column_width=True)

            st.subheader("🖼️ Student Schedule (by Name)")
            st.image(Image.open(students_img_path), caption="Student Schedule by Name", use_column_width=True)

        except Exception as e:
            st.error(f"❌ Error while generating schedule images: {e}")

    else:
        st.error("❌ Failed to generate a valid schedule after 1000 attempts.")
