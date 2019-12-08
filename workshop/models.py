import pandas as pd


MIN_PPL = 125
MAX_PPL = 300


def baseline(data):

    # family indexed
    choices = data[[col for col in data.columns if "choice_" in col]]   # families' preferences
    sizes = data["n_people"]    # families' sizes
    assignments = pd.Series(name="assigned_day")   # holds assigned day for each family
    # day indexed
    potentials = pd.Series(0, index=range(1, 101))  # max number of people possibly attending for each day
    occupancies = pd.Series([0] * 100, index=range(1, 101))   # holds number of people per day

    # STEP 1 : initialize potentials
    for fam, fam_choices in choices.iterrows():
        potentials.loc[fam_choices] += sizes.loc[fam]
    potentials = potentials.sort_values(ascending=True)

    # STEP 2 : fill at least MIN_PPL for each day starting by least wanted days
    for day, _ in potentials.iteritems():

        possible_families = choices[choices == day].dropna(how="all").index.tolist()

        for fam in possible_families:
            if fam not in assignments.index:
                assignments.loc[fam] = day
                occupancies.loc[day] += sizes.loc[fam]
            if occupancies.loc[day] > MIN_PPL:
                break

    # STEP 3 : assign remaining families with their most wanted choice (if possible)
    remaining_fam_choices = choices.loc[~choices.index.isin(assignments.index)]

    for fam, fam_choices in remaining_fam_choices.iterrows():
        for day in fam_choices:
            if occupancies.loc[day] + sizes.loc[fam] <= MAX_PPL:
                assignments.loc[fam] = day
                occupancies.loc[day] += sizes.loc[fam]
                break

    assignments = assignments.reset_index().rename({"index": "family_id"}, axis=1)
    return assignments
