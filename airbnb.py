# Airbnb Data Project
# Table of Contents
# Assignment
# Data Exploration
# searches Dataset
# Distributions
# contacts Dataset

# Import libraries/dataset
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Read datasets
contacts_file = "contacts.tsv"
contacts = pd.read_csv(contacts_file, sep="\t")

searches_file = "searches.tsv"
searches = pd.read_csv(searches_file, sep="\t")

# Find % of null values in datasets
print('Contacts')
print(contacts.isna().sum() / len(contacts), '\n')
print('Searches')
print(searches.isna().sum() / len(searches))

# Drop filter_neighborhoods column
searches = searches.drop(columns=['filter_neighborhoods'])

# Manipulation of searches dataset
# Convert date columns to datetime data type
searches['ds'] = pd.to_datetime(searches['ds'])
searches['ds_checkin'] = pd.to_datetime(searches['ds_checkin'])
searches['ds_checkout'] = pd.to_datetime(searches['ds_checkout'])

# How soon they want the room
searches['length_preperation'] = searches['ds_checkin'] - searches['ds']

# Describe searches dataset
print(searches.describe())

# Calculate skewness in searches dataset
print(searches.skew(axis=0, numeric_only=True, skipna=True))

# Distribution plots of n_guests_min and n_guests_max
sns.displot(searches, x='n_guests_min', color='brown')
sns.displot(searches, x='n_guests_max', color='black')
plt.show()

# When were searches conducted
ax = sns.displot(searches, x='ds', color='brown')
[plt.setp(ax.get_xticklabels(), rotation=90) for ax in ax.axes.flat]
plt.show()

# Percentage of dataset with a filter_price_max above 600
print(len(searches[searches['filter_price_max'] > 600]) / len(searches['filter_price_max']) * 100, '%')

# Distribution of filter_price_max of searches
searches_maxprice_removed = searches[searches['filter_price_max'] <= 600]
sns.displot(x=searches_maxprice_removed["filter_price_max"], color='blue')
plt.show()

# Distribution of length_preperation of searches
distribution = searches["length_preperation"] / np.timedelta64(1, 'D')
print(len(distribution[distribution > 100]) / len(distribution) * 100, '% \n')
distribution = distribution[distribution < 100]
sns.displot(x=distribution, color='green')
plt.show()

# Distribution of n_nights of searches
print(len(searches[searches['n_nights'] > 20]) / len(searches['n_nights']) * 100, '% \n')
searches_within_twenty = searches[searches['n_nights'] < 20]
sns.displot(searches_within_twenty, x='n_nights', color='red')
plt.show()

# Distribution of months of ds_checkin of searches
checkin_month = pd.DatetimeIndex(searches['ds_checkin']).month
sns.displot(checkin_month, color='yellow')
plt.show()

# Types of rooms searched for
print(searches['filter_room_types'].unique()[0:15])

# Find top 15 countries where searches originate from
search_origin = searches.groupby("origin_country").agg({'origin_country': 'count'})
search_origin.columns = ['count']
search_origin = search_origin.sort_values('count', ascending=False)
print(search_origin.nlargest(15, 'count'))

# Manipulation of contacts dataset
# Convert date columns to datetime data type
contacts['ts_contact_at'] = pd.to_datetime(contacts['ts_contact_at'])
contacts['ts_reply_at'] = pd.to_datetime(contacts['ts_reply_at'])
contacts['ts_accepted_at'] = pd.to_datetime(contacts['ts_accepted_at'])
contacts['ts_booking_at'] = pd.to_datetime(contacts['ts_booking_at'])
contacts['ds_checkin'] = pd.to_datetime(contacts['ds_checkin'])
contacts['ds_checkout'] = pd.to_datetime(contacts['ds_checkout'])
contacts['accepted'] = np.where(np.isnan(contacts['ts_accepted_at']), False, True)

contacts['length_stay'] = contacts['ds_checkout'] - contacts['ds_checkin']

# Understand dataset
print(contacts.dtypes)
print(contacts.describe())

# Calculate skewness in contacts dataset
print(contacts.skew(axis=0, numeric_only=True, skipna=True))

# Number of guests stayed
contacts_less8 = contacts[contacts['n_guests'] < 8]
sns.displot(contacts_less8, x='n_guests', hue='accepted', multiple="dodge")
plt.show()

# Conversion rate from accepting to booking
print(contacts['ts_booking_at'].count() / contacts['ts_accepted_at'].count())

# Timeframe of when guests or accepted vs rejected
contacts['month_checkin'] = contacts['ds_checkin'].dt.month
contacts_checkin = contacts[contacts['month_checkin'] > 9]
sns.displot(contacts_checkin, x='month_checkin', hue='accepted', multiple="dodge")
plt.xticks([10, 11, 12])
plt.show()

# Merge datasets for more analysis
merged_datasets = contacts.merge(searches, left_on='id_guest', right_on='id_user')

# Check difference between prices searched between accepted/rejected applicants
merged_pricemax_filter = merged_datasets.loc[(merged_datasets['filter_price_max'] <= 600)]
sns.displot(merged_pricemax_filter, x="filter_price_max", hue="accepted", multiple="dodge")
plt.show()

# Classify dataset based on filter_price_max
def label_price(row):
    if (row['filter_price_max'] >= 0) & (row['filter_price_max'] < 100):
        return '0-100'
    elif (row['filter_price_max'] >= 100) & (row['filter_price_max'] < 200):
        return '100-200'
    elif (row['filter_price_max'] >= 200) & (row['filter_price_max'] < 300):
        return '200-300'
    elif (row['filter_price_max'] >= 300) & (row['filter_price_max'] < 400):
        return '300-400'
    elif (row['filter_price_max'] >= 400) & (row['filter_price_max'] < 500):
        return '400-500'
    elif (row['filter_price_max'] >= 500) & (row['filter_price_max'] < 600):
        return '500-600'
    else:
        return '600+'

merged_datasets['classification_max_price'] = merged_datasets.apply(lambda row: label_price(row), axis=1)
print(merged_datasets.groupby('classification_max_price').agg({'accepted': 'mean'}))

# Find the acceptance rate by country
dataset_country = merged_datasets[['origin_country', 'accepted']]
accepted_count = dataset_country.groupby(['origin_country', 'accepted']).agg({'origin_country': 'count'})
accepted_count.columns = ['count_accepted']
country_count = dataset_country.groupby(['origin_country']).agg({'origin_country': 'count'})
country_count.columns = ['count_country']
acceptance_country = pd.merge(dataset_country, accepted_count, how='left', on=['origin_country', 'accepted'])
acceptance_country = acceptance_country.drop_duplicates()
acceptance_country = pd.merge(acceptance_country, country_count, how='left', on=['origin_country'])
acceptance_country = acceptance_country.sort_values(['count_country', 'accepted'], ascending=[False, True])
acceptance_country = acceptance_country[acceptance_country['count_country'] >= 100]
acceptance_country = acceptance_country[acceptance_country['accepted'] == True]
acceptance_country['acceptance_rate'] = acceptance_country['count_accepted'] / acceptance_country['count_country']
acceptance_country = acceptance_country.sort_values(['acceptance_rate'], ascending=True)
print(acceptance_country)

# Plot the acceptance rate by country
plt.figure(figsize=(12, 8))
sns.barplot(data=acceptance_country, x='origin_country', y='acceptance_rate', palette='viridis')
plt.xticks(rotation=90)
plt.title('Acceptance Rate by Country')
plt.xlabel('Country')
plt.ylabel('Acceptance Rate')
plt.show()

# Saving the data to a new CSV file
acceptance_country.to_csv('acceptance_rate_by_country.csv', index=False)

print("Script executed successfully.")
