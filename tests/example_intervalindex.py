import pandas as pd

dfa = pd.DataFrame.from_dict({
    "ip_address": [13, 5, 20, 11]
})

print(dfa)

dfb = pd.DataFrame.from_dict({
    "lowerbound": [0, 11],
    "upperbound": [10, 20],
    "country": ["australia", "china"]
})
print(dfb)

s = pd.IntervalIndex.from_arrays([0, 11], [10, 20],
                                 closed='both')

dfb = dfb.set_index(s)
print(dfb)

dfa = dfa.assign(country=dfb.loc[dfa['ip_address']].country.values)

print(dfa)
