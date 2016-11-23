#!/usr/bin/env python

# Script to convert game event ID stored in MongoDB to Pandas dataframe for analysis

# TODO: Visualize each event as an image, potentially?


##########################################################################
## Imports
##########################################################################
import pprint
import pandas as pd
import numpy as np
import os
import glob

##########################################################################
## Initial file parameters setup and initialization.
##########################################################################

#Remember to unpack all the .csv files into the data folder of nba_tracking

mydir = "C:\\Users\\Josh\\Documents\\nba-tracking" #Make sure to change to your directory
os.chdir(mydir)

#Find list of csvs, the 41 spurs games, to be converted to dataframe and manipulated at a later step.

filenames = glob.glob(mydir + "\\data\\*.csv")

        

##########################################################################
## Function Design
##########################################################################    
    
#As we ingest our dataframes it would be helpful to reduce dimensions to a set number of obs per instance. Subsample does so.
#Does pivot work for nulls?
    
           
def subsample(df):
    #drop off other things?
    
    #Creates a Group by object (which includes an index separated into groups that restart once a new group begins, enabling aggregate functions)
    g = df.groupby(['event_id', 'PlayerName'])
    
    #first filter step, reduce dimensions by 8, dropping observations from 25 to 3 a second.
    g = df[g.cumcount()%8==0].groupby(['event_id', 'PlayerName'])
                 #is there someway to do this comparison within the g object?
                 #cumulative count returns a dataframe instead of an indexed object, so its difficult to do the divide by 8 filtering in that step
                  
    #Reduce dimensions in filter step 2, only taking 30 obs per player per play
    df_filter = g.tail(30)
    #need to great another g index for the cumulative count per group
    g = df_filter.groupby(['event_id', 'PlayerName'])
    df_filter['obs_in_event'] = (30-g.cumcount())
    
    #! Returns only the columns we were focusing on...for now. Restricted to these columns for computational reasons. 
    #Can merge in shotclocks and other info in a merge relatively easily. Pivot is comp expensive so we want to save columns
    df_filter = df_filter[['game_id', 'event_id', 'PlayerName', 'obs_in_event', 'x_loc', 'y_loc']]
    return df_filter

#Primary execution function utilized to iterate through the list of filenames and concatenate the multiple dataframes into
#some concatenated dataframe
def pivoted_dataframe(filename):
    headers = ["index", "team_id", "player_id", "x_loc", "y_loc", "radius", "moment",
               "game_clock", "shot_clock", "event_id", "game_date", "game_id", "PlayerName"]
    list_ = []
    for filename in filenames:
        df = pd.read_csv(filename,index_col=None, header=0, names=headers)
        #calling our subsample
        df_filter = subsample(df)
        print(filename)
        #pivoting twice to generate wide format for all players in once instance
        pivot1 = df_filter.pivot_table(index=['game_id', 'event_id', 'PlayerName'], columns='obs_in_event') #datatype issue for pivot?
        pivot1.reset_index(inplace=True)  
        pivot2 = pivot1.pivot_table(index=['game_id', 'event_id'], columns='PlayerName')
        pivot2.reset_index(inplace=True)  
        list_.append(pivot2)
        
    frame = pd.concat(list_)
    frame.to_csv('MainFrame_SportVU.csv', index=False)#  +! Pickle the dataframe as an output, or simply reoutput as csv?
    #return frame
    # Reoutput for csv involves: mkdir within data called 'instance_pivot'
##########################################################################
## Execute
##########################################################################    
pivoted_dataframe(filenames) #multiindex filename performance?

    
##########################################################################
## Scrap
##########################################################################        

#Check the number of observations per player, per play
#df[['col1', 'col2', 'col3', 'col4']].groupby(['col1', 'col2']).agg(['mean', 'count'])

# http://stackoverflow.com/questions/11786157/if-list-index-exists-do-x


"""
### Grab every nth item 10x times (if available)
GroupBy.count() 	Compute count of group, excluding missing values
GroupBy.cumcount([ascending]) 	Number each item in each group from 0 to the length of that group - 1.
GroupBy.first() 	Compute first of group values
GroupBy.head([n]) 	Returns first n rows of each group.
GroupBy.last() 	Computse last of group values
GroupBy.max() 	Compute max of group values
GroupBy.mean(\*args, \*\*kwargs) 	Compute mean of groups, excluding missing values
GroupBy.median() 	Compute median of groups, excluding missing values
GroupBy.min() 	Compute min of group values
GroupBy.nth(n[, dropna]) 	Take the nth row from each group if n is an int, or a subset of rows if n is a list of ints.
"""


#remove later, just to test def subsample

headers = ["index", "team_id", "player_id", "x_loc", "y_loc", "radius", "moment", \
           "game_clock", "shot_clock", "event_id", "game_date", "game_id", "PlayerName"]
df = pd.read_csv(filenames[0], names=headers)

g = df.groupby(['event_id', 'PlayerName'])
#first filter step, reduce dimensions by 8 as we have 25 obs per second per player!
g = df[g.cumcount()%8==0].groupby(['event_id', 'PlayerName'])
              #g[] vs df[]? 
              

#Reduce dimensions in filter step 2, only taking 30 obs per player per play
df_filter = g.tail(30)
#need to great another g index for the cumulative count per group
g = df_filter.groupby(['event_id', 'PlayerName'])
df_filter['obs_in_event'] = (30-g.cumcount()) #?! Fix this shit
#Backwards index for pivot?
df_filter.head(100) #ix to print?    
df_filter.columns.values
df_filter = df_filter[['PlayerName', 'x_loc', 'y_loc', 'shot_clock', 'event_id', 'obs_in_event']]
pivot1 = df_filter.pivot_table(index=['PlayerName','event_id'], columns='obs_in_event')
pivot2 = pivot1
pivot2.reset_index(inplace=True)  
pivot2.to_csv('frametest.csv', index=False)
