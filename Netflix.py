#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
import seaborn as sns
from datetime import datetime

import warnings
warnings.filterwarnings("ignore")


# In[2]:


df=pd.read_csv(r"D:\Tableau\Netflix\netflix_titles.csv",encoding="ISO-8859-1")


# In[3]:


df.head()


# In[4]:


df.tail()


# In[5]:


print("Shape:",df.shape,"\n")
print("Null values:","\n",df.isna().sum())


# In[6]:


df.dtypes


# In[7]:


for i in df.columns:
    print("Column Names",i,"has total unique values",len(df[i].unique()))
    print(df[i].unique())
    print("-"*120)


# In[8]:


print("Minimum:",min(df.release_year))
print("Maximum:",max(df.release_year))


# In[9]:


#Categories of diff types
df["type"].unique()


# In[10]:


#Different age rating
df["rating"].unique()


# In[11]:


#Diff genre
genre_list=pd.unique(df.listed_in.str.split(",",expand=True).stack())
for i in range(len(genre_list)):
    genre_list[i]=genre_list[i].strip()
    
genre_list=list(pd.unique(genre_list))
genre_list


# In[12]:


df.loc[df["director"]=="nan"]


# <u>**Observations**<u>
# 
# - Scope of the data is from the year 1925 to 2021.
# - There are no duplicates in the data.
# - Column 'date_added' should be conveverted into datetime datatype.
# - Highest number of null values are present in the director column followed by cast country and date_added
# - Rating columns has 'NR'(not rated) , 'UR'(unrated) are practically the same thing, this must be resloved.
# - date_added column could be futher divided into new colums based on year and month
# - Listed_in column should be renamed to 'Genre' for ease

# # Cleaning

# In[13]:


#Remove Whitespace from columns containing strings

columns=list(df.columns)
columns.remove("release_year")

for i in columns:
    df[i]=df[i].str.strip()


# In[14]:


#Replacing nan with "" in string datatype columns
str_cols=["director","cast","country","date_added","rating"]

for column in str_cols:
    df[column]=df[column].fillna("")


# In[15]:


df.isnull().sum()


# In[16]:


#Renaming listed_in column
df=df.rename(columns={"listed_in":"Genre"})


# In[17]:


df.columns


# <u>**Fixing Rating Column**<u>

# In[18]:


#Adding all the columns with rating "UR" into "NR"
for i in range(len(df)):
    if df["rating"].iloc[i]== 'UR':
        df["rating"].iloc[i]= 'NR'
        
#Making sure it worked
df["rating"].unique()


# In[19]:


#Inspecting columns with "77 min", "66 min", "84 min" rating 
wrong_rating=["74 min","84 min","66 min"]
for i in range(len(df)):
    if df["rating"].iloc[i] in wrong_rating:
        print(df.iloc[i])


# In[20]:


cell_1=df.loc[df["rating"]=="74 min"]
cell_2=(df.loc[df["rating"]=="84 min"])
cell_3=(df.loc[df["rating"]=="66 min"])


# In[21]:


weird_rating=pd.concat([cell_1,cell_2,cell_3])


# In[22]:


weird_rating


# From this we can see that wrong rating actually belongs to duration column.

# In[23]:


#Moving wrong rating to duration
index=[5541,5794,5813]

for i in index:
    x=df["rating"].iloc[i].split(" ")
    du=x[0]
    df["duration"].iloc[i]=du
    df["rating"].iloc[i]="NR"
    
    
 #Checking
for i in index:
    print(df.iloc[i])


# **<u>Splitting Date added into multiple columns<u>**

# In[24]:


df["date_added"].isna().sum()


# In[25]:


(df["date_added"]=="").sum()


# In[26]:


#Rows with null values
null_rows=[]
for i in range(len(df)):
    if df["date_added"].iloc[i]=="":
        null_rows.append(i)


# In[27]:


#Months and Year
month_added=[]
year_added=[]

for i in range(len(df)):
    #replacing nan with 0
    if i in null_rows:
        month_added.append(0)
        year_added.append(0)
    else:
        date=df["date_added"].iloc[i].split(" ")
        month_added.append(date[0])
        year_added.append(date[2])
        
        
#Turning month into month number
for i, month in enumerate(month_added):
    if month != 0:
        datetime_obj=datetime.strptime(month,"%B")
        month_number =datetime_obj.month
        month_added[i]=month_number
        
#Checking
print(set(month_added))
print(set(year_added))

#inserting new columns into the dataframe

df.insert(7,"month_added",month_added,allow_duplicates=True)
df.insert(8,"year_added",year_added,allow_duplicates=True)


# **<u>Getting a list of Countries<u>**

# In[28]:


#creating a function obtain unique values from columns containing strings
def getset(data):
    data_list=set()
    for v in data:
        values=v.split(", ")
        for i in values:
            data_list.add(i)
    return list(data_list)


# In[29]:


country_list=getset(df["country"])
country_list


# <u>**Dropping columns not Required**<u>

# In[30]:


df=df.drop(columns=["description","cast"])
df


# # ANALYSIS

# <u>**Ratio of Shows vs Movies**<u>

# In[31]:


df["type"].value_counts()


# In[32]:


plt.figure(figsize=(7,5))
sns.countplot(x="type",data=df,palette="BuPu")
plt.xlabel("Type")
plt.ylabel("Frequency")
plt.title("Histogram for types")
plt.show()


# In[33]:


X=df["type"].value_counts()
Movies=X[0]
TV_shows=X[1]

#Creating pie chart
ax=plt.subplots(figsize=(15,8)) 
explode=[0,0.1]
color=["blue","green"]
slices=[Movies,TV_shows]
labels=["Movies","TV_shows"]

plt.pie(slices,labels=labels,colors=color,explode=explode,autopct="%1.1f%%")
plt.legend()


# In[34]:


ax=plt.subplots(figsize=(15,8))
sns.countplot(data=df,x="year_added",palette="rainbow_r")


# Some of Oldest TV shows and Movies

# In[35]:


oldies=df.sort_values("release_year",ascending=True)
oldies[["title","release_year"]].head(15)


# In[36]:


plt.figure(figsize=(100,20))
sns.countplot("country",data=df,palette="turbo")
plt.xticks(rotation=90)
plt.show()


# In[37]:


countries=df.country.value_counts()
countries


# In[38]:


def getlist(data):
    data_list=list()
    for v in data:
        values=v.split(", ")
        for i in values:
            data_list.append(i)
    return list(data_list)

#Counting occurence of each countryname
country_list=getlist(df["country"])
country_count=pd.value_counts(country_list).to_frame(name="Occurence").reset_index()
country_count.head(15)

#the empty value is count of shows where country was not mentioned


# Popular Directors by amount of content

# In[39]:


director_list=getlist(df["director"])
director_count=pd.value_counts(director_list).to_frame(name="Occurence").reset_index()
director_count.head(10)


# In[40]:


genre_list=getlist(df["Genre"])
pd.value_counts(genre_list).to_frame(name="Total").reset_index()


# In[ ]:




