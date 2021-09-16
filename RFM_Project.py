import matplotlib.pyplot as plt
import datetime as dt
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

###################################
# TASK 1 : Understanding and Preparing Data
###################################

# Please read the 2010-2011 data in Online Retail II excel. Create a copy of the dataframe that you created.

df_ = pd.read_excel("Datasets/online_retail_II.xlsx", sheet_name="Year 2010-2011")
df = df_.copy()

# Examine the descriptive statistics of the dataset.

df.describe().T
df["Price"].mean()
df["Price"].median()

df["Quantity"].mean()
df["Quantity"].median()

df["Price"][df["Price"]<1000].hist(bins=50)
plt.show()

# Are there any missing observations in the dataset? How many missing observations are there in which variable, if any?

df.isnull().values.any()
df.isnull().sum()

# Remove missing observations from the dataset. In the extraction process, use the’ inplace=True ' parameter.

df.dropna(inplace=True)

# What is the number of unique products?

df["Description"].nunique()

# How many products are there?

df.groupby("Description").agg({"Description": "count"})

# Sort the 5 most ordered products to the minimum already.

df.groupby("Description").agg({"Quantity": "sum"}).sort_values("Quantity", ascending=False).head()

# The ‘C’ on the invoices shows the canceled transactions. Remove the canceled transactions from the data set.

df = df[~df["Invoice"].str.contains("C", na=False)]
df.head()

# Create a variable called ‘TotalPrice’ that expresses the total earnings per invoice.

df = df[(df["Quantity"]>0)]
df = df[(df["Price"]>0)]

df["TotalPrice"] = df["Quantity"] * df["Price"]

###################################
# TASK 2 : Creating RFM scores and converting them into a single variable
###################################

# ▪ Define Recency, Frequency and Monetary.
# ▪ Calculate the Recency, Frequency and Monetary metrics with groupby, agg and lambda in a customer-specific way.
# ▪ Assign the calculated metrics to a variable called rfm.
# ▪ Change the names of the metrics you create to recency, frequency, and monetary.

df["InvoiceDate"].max()
today_date = dt.datetime(2011, 12, 11)

rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda date : (today_date - date.max()).days,
                                     'Invoice': lambda num: num.nunique(),
                                     'TotalPrice': lambda TotalPrice: TotalPrice.sum()})


rfm.columns = ['recency', 'frequency', 'monetary']
rfm = rfm[rfm["monetary"] > 0]
rfm.head()

###################################
# TASK 3 : Creating RFM scores and converting them into a single variable
###################################

# ▪ Convert the Recency, Frequency and Monetary metrics to scores between 1-5 with the help of qcut.Decency, Frequency and
# Monetary metrics.
# ▪ Save these scores as recency_score, frequency_score and monetary_score.
# ▪ Express the value of 2 different variables as a single variable and save it as RFM_SCORE.

rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

rfm["recency_score"].value_counts()
rfm["frequency_score"].value_counts()
rfm["monetary_score"].value_counts()

rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                    rfm['frequency_score'].astype(str))

rfm["RFM_SCORE"].head()


###################################
# TASK 4 : Defining RFM scores as segments
###################################

# ▪ Make segment definitions so that the generated RFM scores are more understandable.
# ▪ Convert the scores into segments using the following seg_map.

seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)
rfm['segment'].head()

###################################
# TASK 5 : Time for Action
###################################

# ▪ Select the 2 segments that you find important. These two segments are;
# - Both in terms of action decisions,
# - Please interpret it both in terms of the structure of the segments (average RFM values).
# ▪ Select the customer IDs belonging to the "Loyal Customers" class and extract the excel output.

rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count","max"])

"""
-champions:
# there are 633 people in this segment,
# on average, the last purchases took place 6 days ago,
# shopping frequencies are 12, there are 209 purchases in total,
# 6857.96 / TL expenses have been incurred.

-- >customers in the champions segment have recently made purchases, often make high-volume purchases 
they are customers. Considering that a part of the earned income comes from these customers, we offer them special 
personal campaigns by editing, loyalty rates can be increased and customers in this segment can be used to increase recognition.

- loyal_customers:
# there are 819 people in this segment,
# on average, the last purchases took place 33 days ago,
# shopping frequencies are 6, there are 63 purchases in total,
# 2864.24 / TL expenses have been incurred.

-- >customers in the loyal_customers segment have higher shopping frequencies than in the champions segment. Loyalty of
loyal customers it's important to protect it.With this in mind, by introducing new products similar to the products that 
loyal customers are most interested in, their purchase frequency can be further increased by creating campaigns.
In this way, it is shortened between dec last purchases and the previous purchases. 

"""


new_df = pd.DataFrame()
new_df["loyal_customers"] = rfm[rfm["segment"] == "loyal_customers"].index
new_df.head()

new_df.to_excel("loyal_customers.xlsx")
