import pandas as pd

# Example DataFrame
df = pd.DataFrame(columns=['A', 'B'])
# Example dictionary to append
dict_to_append = {'A': 1, 'B': 2}

# Attempt to append
df = df.append(dict_to_append, ignore_index=True)
print(df)