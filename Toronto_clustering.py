#!/usr/bin/env python
# coding: utf-8

# PART I: Import from Wikipedia List of postal codes of Canada and create a DF

# In[1]:


import pandas as pd
import requests
from pandas.io.json import json_normalize

import folium


# In[2]:


url = "https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M"
table = pd.read_html(url)[0]


# In[3]:


table.info()


# In[4]:


table = table[table['Borough']!='Not assigned'] #Drop the rows that contatins the "Not assigned" in the column "Borough"


# In[5]:


table.head()


# In[6]:


table = table.groupby(['Postcode', 'Borough'],as_index=False).agg(', '.join) #Aggregate rows with same Postcode


# In[7]:


table[table['Borough'].str.contains('Queen')]


# In[8]:


#create a function for change "Not assigned" in the "Neighbourhood" for the Borough´s name

def __assigned__(x, y):
    if y == "Not assigned":
        return x
    else:
        return y    


# In[9]:


x = table

table["Neighbourhood"] = table.apply(lambda x: __assigned__(x["Borough"], x["Neighbourhood"]), axis=1)


# In[10]:


table[table['Borough'].str.contains('Queen')] #Verify that all be ok.


# In[11]:


table.shape


# Part II: Getting the Geolocations

# In[ ]:





# In[12]:


geo_coordinates = pd.read_csv('Geospatial_Coordinates.csv')


# In[13]:


geo_coordinates.head()


# In[14]:


df = table.merge(geo_coordinates, left_on='Postcode', right_on='Postal Code').drop(['Postal Code'], axis=1)
df.head()


# In[31]:


def getNearbyVenues(names, latitudes, longitudes, radius=500):
    
    venues_list=[]
    for name, lat, lng in zip(names, latitudes, longitudes):
        print(name)
            
        # create the API request URL
        url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
            CLIENT_ID, 
            CLIENT_SECRET, 
            VERSION, 
            lat, 
            lng, 
            radius, 
            LIMIT)
            
        # make the GET request
        results = requests.get(url).json()["response"]['groups'][0]['items']
        
        # return only relevant information for each nearby venue
        venues_list.append([(
            name, 
            lat, 
            lng, 
            v['venue']['name'], 
            v['venue']['location']['lat'], 
            v['venue']['location']['lng'],  
            v['venue']['categories'][0]['name']) for v in results])

    nearby_venues = pd.DataFrame([item for venue_list in venues_list for item in venue_list])
    nearby_venues.columns = ['Neighborhood', 
                  'Neighborhood Latitude', 
                  'Neighborhood Longitude', 
                  'Venue', 
                  'Venue Latitude', 
                  'Venue Longitude', 
                  'Venue Category']
    
    return(nearby_venues)


# Part III: Working with the data

# In[32]:


df_toronto = df[df['Borough'].str.contains('Toronto')]
df_toronto.head()


# In[33]:


latitude = 43.6532
longitude = -79.3832
print('The geograpical coordinate of Toronto are {}, {}.'.format(latitude, longitude))


# In[34]:


map_toronto = folium.Map(location=[latitude, longitude], zoom_start=11)

# add markers to map
for lat, lng, label in zip(df_toronto['Latitude'], df_toronto['Longitude'], df_toronto['Neighbourhood']):
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=label,
        color='blue',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7,
        parse_html=False).add_to(map_toronto)  
    
map_toronto


# In[ ]:





# In[35]:


CLIENT_ID = 'WNU4QNPM0NESFXS5PNS4FVNI2LXWXV3F5AVCX2UTZDEZYS5H' # your Foursquare ID
CLIENT_SECRET = 'NY50BSQ1QWU3RAXCKQNFBWIEISZOG2KSYPOKXN40JJFPJ0G2' # your Foursquare Secret
VERSION = '20180604'
LIMIT = 50
print('Your credentails:')
print('CLIENT_ID: ' + CLIENT_ID)
print('CLIENT_SECRET:' + CLIENT_SECRET)


# In[36]:


## By search query ##


# In[37]:


search_query = 'Gym'
radius = 5000
print(search_query + ' .... OK!')


# In[38]:


url = 'https://api.foursquare.com/v2/venues/search?client_id={}&client_secret={}&ll={},{}&v={}&query={}&radius={}&limit={}'.format(CLIENT_ID, CLIENT_SECRET, latitude, longitude, VERSION, search_query, radius, LIMIT)
url


# In[39]:


results = requests.get(url).json()
results


# In[40]:


venues = results['response']['venues']

# tranform venues into a dataframe
dataframe = json_normalize(venues)
dataframe.head()


# In[41]:


# keep only columns that include venue name, and anything that is associated with location
filtered_columns = ['name', 'categories'] + [col for col in dataframe.columns if col.startswith('location.')] + ['id']
dataframe_filtered = dataframe.loc[:, filtered_columns]

# function that extracts the category of the venue
def get_category_type(row):
    try:
        categories_list = row['categories']
    except:
        categories_list = row['venue.categories']
        
    if len(categories_list) == 0:
        return None
    else:
        return categories_list[0]['name']

# filter the category for each row
dataframe_filtered['categories'] = dataframe_filtered.apply(get_category_type, axis=1)

# clean column names by keeping only last term
dataframe_filtered.columns = [column.split('.')[-1] for column in dataframe_filtered.columns]

dataframe_filtered.head()


# In[42]:


dataframe_filtered.name.head()


# In[43]:


venues_map = folium.Map(location=[latitude, longitude], zoom_start=13) # generate map centred

# add a red circle marker to represent the center
folium.features.CircleMarker(
    [latitude, longitude],
    radius=10,
    color='red',
    popup='Toronto',
    fill = True,
    fill_color = 'red',
    fill_opacity = 0.6
).add_to(venues_map)

# add the venues as blue circle markers
for lat, lng, label in zip(dataframe_filtered.lat, dataframe_filtered.lng, dataframe_filtered.categories):
    folium.features.CircleMarker(
        [lat, lng],
        radius=5,
        color='blue',
        popup=label,
        fill = True,
        fill_color='blue',
        fill_opacity=0.6
    ).add_to(venues_map)

# display map
venues_map


# In[ ]:





# ## Explore & Clustering##

# Part 1

# In[27]:


CLIENT_ID = 'WNU4QNPM0NESFXS5PNS4FVNI2LXWXV3F5AVCX2UTZDEZYS5H' # your Foursquare ID
CLIENT_SECRET = 'NY50BSQ1QWU3RAXCKQNFBWIEISZOG2KSYPOKXN40JJFPJ0G2' # your Foursquare Secret
VERSION = '20180605' # Foursquare API version

print('Your credentails:')
print('CLIENT_ID: ' + CLIENT_ID)
print('CLIENT_SECRET:' + CLIENT_SECRET)


# In[47]:


df_toronto.head()


# In[48]:


latitude = 43.6532
longitude = -79.3832
print('The geograpical coordinate of Toronto are {}, {}.'.format(latitude, longitude))


# In[49]:


map_toronto = folium.Map(location=[latitude, longitude], zoom_start=11)

# add markers to map
for lat, lng, label in zip(df_toronto['Latitude'], df_toronto['Longitude'], df_toronto['Neighbourhood']):
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=label,
        color='blue',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7,
        parse_html=False).add_to(map_toronto)  
    
map_toronto


# In[ ]:





# In[50]:


CLIENT_ID = 'WNU4QNPM0NESFXS5PNS4FVNI2LXWXV3F5AVCX2UTZDEZYS5H' # your Foursquare ID
CLIENT_SECRET = 'NY50BSQ1QWU3RAXCKQNFBWIEISZOG2KSYPOKXN40JJFPJ0G2' # your Foursquare Secret
VERSION = '20180605' # Foursquare API version

print('Your credentails:')
print('CLIENT_ID: ' + CLIENT_ID)
print('CLIENT_SECRET:' + CLIENT_SECRET)


# In[ ]:





# Part 2 Explore Neighborhoods

# In[99]:


def getNearbyVenues(names, latitudes, longitudes, radius=500):
    
    venues_list=[]
    for name, lat, lng in zip(names, latitudes, longitudes):
        print(name)
            
        # create the API request URL
        url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
            CLIENT_ID, 
            CLIENT_SECRET, 
            VERSION, 
            lat, 
            lng, 
            radius, 
            LIMIT)
            
        # make the GET request
        results = requests.get(url).json()["response"]['groups'][0]['items']
        
        # return only relevant information for each nearby venue
        venues_list.append([(
            name, 
            lat, 
            lng, 
            v['venue']['name'], 
            v['venue']['location']['lat'], 
            v['venue']['location']['lng'],  
            v['venue']['categories'][0]['name']) for v in results])

    nearby_venues = pd.DataFrame([item for venue_list in venues_list for item in venue_list])
    nearby_venues.columns = ['Neighborhood', 
                  'Neighborhood Latitude', 
                  'Neighborhood Longitude', 
                  'Venue', 
                  'Venue Latitude', 
                  'Venue Longitude', 
                  'Venue Category']
    
    return(nearby_venues)


# In[100]:


toronto_venues = getNearbyVenues(names=df_toronto['Neighbourhood'],
                                   latitudes=df_toronto['Latitude'],
                                   longitudes=df_toronto['Longitude']
                                  )


# In[ ]:





# In[101]:


print(toronto_venues.shape)
toronto_venues.head()


# In[103]:


toronto_venues1 = toronto_venues


# In[104]:


toronto_venues1.groupby('Neighborhood').count()


# In[105]:


print('There are {} uniques categories.'.format(len(toronto_venues1['Venue Category'].unique())))


# In[ ]:





# Part 3

# In[106]:


# one hot encoding
toronto_onehot = pd.get_dummies(toronto_venues1[['Venue Category']], prefix="", prefix_sep="")

# add neighborhood column back to dataframe
toronto_onehot['Neighborhood'] = toronto_venues1['Neighborhood'] 

# move neighborhood column to the first column
fixed_columns = [toronto_onehot.columns[-1]] + list(toronto_onehot.columns[:-1])
toronto_onehot = toronto_onehot[fixed_columns]

toronto_onehot.head()


# In[ ]:





# In[ ]:




