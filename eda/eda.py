from matplotlib import pyplot as plt

from util import get_df

df = get_df()

df["netloc"].map(
    lambda d: "apm.activecommunities.com" if "anc.apm" in d else d
).value_counts().plot(kind="pie", title="URL breakdown", ylabel="")
plt.show()
