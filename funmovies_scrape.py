#import all necessary labraries
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np
#importing extra module
import random,time
from wordcloud import WordCloud
from matplotlib import pyplot as plt

##list of url to fetch data from
data_locations=['https://www.justwatch.com/in/movies?release_year_from=2000','https://www.justwatch.com/in/tv-shows?release_year_from=2000']
df_lst=[]       #**stores both tv and movies dataframe


for i in range(2):                                 #loop for movie and tv show section
  entry_url=data_locations[i]
  page=requests.get(entry_url)                      # Sending an HTTP GET request to the URL
  entry_soup=BeautifulSoup(page.text,'html.parser') # Parsing the HTML content using BeautifulSoup with the 'html.parser'
  print(entry_soup.prettify())

  # Write Your Code here
  url_collection=[]       #'''stores links to scrape data'''
  url_prefix='https://www.justwatch.com'
  for a in entry_soup.find_all('a',class_='title-list-grid__item--link'):
    url_collection.append(url_prefix+a['href'])
    if len(url_collection)==80:                     #limitimg scraping of only 80 movies
      break
  print('Total:'+str(len(url_collection)))

  show_release=[]         #release year list
  show_title=[]           #name of movie or show
  faild_url=[None]
  pcountry=[]             #country where it was produced 
  Age_Rating=[]
  genre=[] 
  rtime=[]                #runtime of each item
  streams=[]              #streaming service available e.g. Netflix
  imbd=[]                 #Rating of each item as on IMDB 

  
  ##genre,age rating,production country,runtime
  def fetch_details(tresp):
    #this function scrapes all 4 elements from single response,thus avoiding repeated calling of recur_get function
    # #'''dt_dct is a dictionary used to store and return required details of an item'''
    
    dt_dct={'Genres':None,'Rating':None,'Production country':None,'Age rating':None,'Runtime':None}
    soup1=tresp.find('div',class_='title-info title-info')

    try:
      dt=soup1.find_all('div',class_='detail-infos',attrs={'data-v-1e997566':False})
      for d in dt:
        heading=d.find('h3',class_="detail-infos__subheading").text
        heading=heading.strip(' ')
        '''this maps each section from details and respectively assigns value to same section in dt_dct dictionary '''
        try:
          dt_dct[heading]=d.find("div",class_="detail-infos__value").text
        except:
          dt_dct[heading]=d.find("span",class_="detail-infos__value").text
          
    except:
      return dt_dct
    return dt_dct           #returns dict of set values only,and none for unset values.


##genre,age rating,production country,runtime
  def fetch_details(tresp):
  #this function scrapes all 4 elements from single response,thus avoiding repeated calling of recur_get function

    #'''dt_dct is a dictionary used to store and return required details of an item'''
    dt_dct={'Genres':None,'Rating':None,'Production country':None,'Age rating':None,'Runtime':None}
    soup1=tresp.find('div',class_='title-info title-info')

    try:
      dt=soup1.find_all('div',class_='detail-infos',attrs={'data-v-1e997566':False})
      for d in dt:
        heading=d.find('h3',class_="detail-infos__subheading").text
        heading=heading.strip(' ')
        '''this maps each section from details and respectively assigns value to same section in dt_dct dictionary '''
        try:
          dt_dct[heading]=d.find("div",class_="detail-infos__value").text
        except:
          dt_dct[heading]=d.find("span",class_="detail-infos__value").text
          
    except:
      return dt_dct
    #**a complete dictionary with all values filled is constructed and returned#
    return dt_dct

    

  def recur_get(tvurli,ts=0):                   #takes url and time delay in seconds as parameters
  ##def this function recursively request url to server with time delay and creates a list of item title
    urli=tvurli
    resp=''
    headers_lst=['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
              'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
              'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.864.48 Safari/537.36 Edg/91.0.864.48',
              'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 OPR/77.0.4054.90',
              'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.48'
  ]
    header=headers_lst[random.randint(0,4)]         #getting random user-agent for each call
    try:
      time.sleep(ts)                                      #keepinngtime gap between each request        
      resp=requests.get(urli,headers={'User-Agent': header})
    except:
      print(resp.status_code)

    return resp if resp.status_code==200 else recur_get(urli,0.4) if resp.status_code==429 else None      #return server response if success else try again
  ##recur_get ends


  #scraping for each web url in the url collection
  for urli in url_collection:   
    print(urli) 

    #time.sleep(0.05)     #interval of 0.8 sec between each request to prevent(429) web server from over-loading
    tvresp=recur_get(urli)    

    try:
      tresponse=BeautifulSoup(tvresp.content,'html.parser')
      soup1=tresponse.find('div',class_='title-block')#attrs={"data-testid":"titleBlock"})
    except (AttributeError):
      show_title.append(None)
      faild_url.append(urli)
      continue
    if soup1:
      ##adding ttitle to title list
      show_title.append(soup1.find('h1').text)
      #print(soup1.find('h1').text)

      ##adding to release year list
      show_release.append(soup1.find('span',class_="text-muted").text)
      #print(soup1.find('h1').text+':'+soup1.find('span',class_="text-muted").text)

      ##scraping genre,age rating,production country and runtime
      details_dct=fetch_details(tresponse)

      Age_Rating.append(details_dct['Age rating'])
      genre.append(details_dct['Genres'])
      pcountry.append(details_dct['Production country'])
      rtime.append(details_dct['Runtime'])
      imbd.append(details_dct['Rating'])

  ##Scraping streaming services
    try:
        stream_div=tresponse.find('div',class_='buybox-row__offers',attrs={'data-v-4ea74991':True})
        stream_box=stream_div.find('img')
    except (IndexError,AttributeError) as e:
      stream_val=None
      continue
    else:
      stream_val=stream_box['alt']
    finally:
        #print(str(stream_val))
        streams.append(stream_val)   
  ##data scraping for both mivies and tv show ends 
  temp_df=pd.DataFrame({'Title':show_title,'Release Year':show_release,'Genre':genre,'Stream Platforms':streams,'Links':url_collection,'Duration':rtime,'Age Rating':Age_Rating,'Production Country':pcountry,'IMDB':imbd})
  df_lst.append(temp_df)
  print(temp_df.head())  
  time.sleep(5)
  del(temp_df)
  del(url_collection)

##Dataframe construction complete
mvdf=df_lst[0]
tvdf=df_lst[1]
##saving both dataframe
mvdf.to_csv('funmovies_movies.csv')
tvdf.to_csv('funmovies_tvs.csv')

#merging datas of both movies and tvs
mvdf['Category']='mv'
tvdf['Category']='tv'
ndf=pd.concat([mvdf,tvdf],axis=0)             ##ndf IS THE NEW COMBINED DATA FRAME...
ndf.index=[i for i in range(ndf.shape[0])]
ndf.to_csv('Final_Funmovies_rawdf.csv')             ##unfiltered dataframe saved


#**DATA FILTERING AND ANALYSIS**#
#a. Filter movies and TV shows based on specific criteria:**

##formating Release year column 
ndf["Release Year"]=ndf['Release Year'].apply(lambda x:int(x.strip(' ')[1:-1]))
ndf['Release Year']=pd.to_datetime(ndf['Release Year'],format='%Y').dt.year
ndf=ndf[ndf['Release Year']>=2022]          #filtering movies and tv show of only 2022 and after


#filtering with IMDB rating > 7
def sfn(s):
    '''this function removes the vote counts from IMDB column'''
    s=s.strip(' ')
    s=s[:3]
    return s
#formatting imdb column just to keep the rating integer value
ndf['IMDB']=ndf['IMDB'][ndf['IMDB'].notnull()].apply(sfn)
ndf['IMDB'] = pd.to_numeric(ndf['IMDB'], errors='coerce')       #**convert all values to float
#filtering data of only IMDB rating above than 7
ndf=ndf[ndf['IMDB']>7]                                           


#b. Data Analysis:**

##AVERAGE IMDB RATING
mean_imdb=np.mean(ndf['IMDB'][ndf['IMDB'].notnull()])
print('Mean IMDB values for both TV and shows is :',mean_imdb)


##TOP GENRE VISUALIZATION
gen_lst=ndf['Genre'].to_list()
genstr=','.join(gen_lst)
genre_wc=WordCloud()
plt.axis('off')
genre_wc.generate(genstr)    #<display of wordcloud>
plt.imshow(genre_wc,interpolation='bilinear')
genre_wc.to_file("Genres Analysis wordcloud.png")     ##wordcloud image saved 
##!!insight
print('We can see from Wordcloud that Drama,Mystery,Thriller,Science and Action genres are predominant')


##Streaming Service with Most offering
print(ndf['Stream Platforms'].value_counts())

#!!Visualization of straming services
strm_wc=WordCloud()
strms_lst=ndf['Stream Platforms'][ndf['Stream Platforms'].notnull()].to_list()
strms_str=",".join(strms_lst)
strm_wc.generate(strms_str)
plt.axis('off')
plt.imshow(strm_wc,interpolation='bilinear')
plt.show()
strm_wc.to_file("Streaming analysis wordcloud.png")
#!!insights
print('Its evident that Amazon Prime Video is the predominant Straming Service in both TV and Movies.')

#print(ndf['Stream Platforms'][ndf['Stream Platforms']=='Netflix'].count())
#ndf['Stream Platforms'].value_counts().plot(kind='bar',yticks=[i for i in range(0,30)],)
max_stream_platform=ndf['Stream Platforms'].value_counts().idxmax()       #get the platform with most apeearance
ndf.groupby('Category')['Stream Platforms'].value_counts().plot(kind='bar',title='Breakdown of Available Streaming Platforms')
print(f'Breakdown of {max_stream_platform} between Movie and Tv show:')
print(ndf[ndf['Stream Platforms']==max_stream_platform].groupby('Category')['Stream Platforms'].value_counts())


#preparing data for exporting
ndf.sort_values(by='Release Year')
ndf.index=[i for i in range(ndf.shape[0])]
ndf.to_csv('Filter_Final_funmovies_data.csv')                  #exported filtered and clean data
          