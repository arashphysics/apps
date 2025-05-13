import streamlit as st
import numpy as np
import pandas as pd

st.title("Lab Schedule Generator")

min_gap = st.slider("Minimum gap between experiments (in weeks):", 1, 5, 1)

if st.button("Generate Schedule"):

    names = [
        "Sam Bennett", "Tyler Bird", "Charles Capiato", "Gabe Cunningham", "Myles Drew",
        "Polina Erofeeva", "Lauren Hall", "Cameron Johnson", "Marshall Hurlbut",
        "Jack Laidlaw", "Karen Magureanu", "Cason Martz", "Sedona Reed", "Paul Reid",
        "Joanna Leith", "Lukas Speier", "Colby Stewart", "Grace Tomasi"
    ]

    week = list(range(1, 10))
    dates = ['May 21', 'May 28', 'June 4', 'June 11', 'June 18', 'June 25', 'July 9', 'July 16', 'July 23']
    expt = ['expt 32', 'expt 33', 'expt 34']

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

                students_sch.loc[student, expt[exp_need]] = f"Week {wk + 1}, {dates[wk]}"
                sch_arr[exp_need, wk] += 1

                if pd.isna(schedule.iloc[exp_need, wk]):
                    schedule.iloc[exp_need, wk] = student
                else:
                    schedule.iloc[exp_need, wk] += ', ' + student

            if not success:
                break

        if success:
            break

    if success:
        st.success(f"✅ Schedule completed after {attempt + 1} attempt(s).")
        schedule.columns = [f"Week {i + 1}, {dates[i]}" for i in range(len(dates))]

        st.subheader("📅 Full Schedule (by Experiment)")
        st.dataframe(schedule.transpose())

        st.subheader("👨‍🎓 Student Schedule (by Name)")
        st.dataframe(students_sch)
    else:
        st.error("❌ Failed to generate a valid schedule after 1000 attempts.")
