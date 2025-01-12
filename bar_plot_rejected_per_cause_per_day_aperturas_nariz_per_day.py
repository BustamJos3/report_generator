#!/usr/bin/env python
# coding: utf-8

# In[204]:


import pandas as pd #modules
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import os
import pathlib
from pathlib import Path
from datetime import datetime


# In[205]:


directory = Path(r".\data_plots") #get current work directory
directory.mkdir(exist_ok=True)
matching_files = list(directory.glob("*obj*.xlsx"))  # Busca archivos que contengan 'obj' y tengan extensión .xlsx
print("Archivos encontrados:", matching_files)


# In[206]:


dict_data_pointer={} #dict to store files as dfs
for i in matching_files: # Read the Excel file 
    file_path = str(i)  # Update this with the path
    df = pd.read_excel(file_path)
    print(file_path)
    df_name=file_path.split("obj_")[1].split(".")[0] #split str with "obj_" and the  "." char and take the file name
    date_col="Fecha" #default col name with dates
    if "aperturas" in file_path.lower(): #if excel name file contains "aperturas", change col name with dates
        date_col="Fecha Paro"
    row_numbers_nan = df.index[df[date_col].isna()].tolist() # Get the row numbers where 'Fecha' or 'Fecha Paro' is NaN
    row_numbers = list(set(row_numbers_nan)) # lists of row with nan numbers
    filtered_df = df.drop(index=row_numbers) # Filter the DataFrame to keep only the rows that are not in row_numbers
    dict_data_pointer[f"{df_name}"]=filtered_df #store filtered df in dictionary data pointer
print(list(dict_data_pointer.keys())) #see keys on dictionary to check callability


# In[207]:


data_pointer_ar="aperturas_nariz" #select df of aperturas de nariz
df_ar=dict_data_pointer[data_pointer_ar] #mask df of aperturas de nariz with alias df_ar
dates_col_name_ar="Fecha Paro" #name of col with dates in df
df_ar[dates_col_name_ar] = df_ar[dates_col_name_ar].astype('str') #convert datetime to str
df_ar[dates_col_name_ar][0]


# In[208]:


df_ar.head()


# In[209]:


time_stamp_dates=list([ i for i in [ df_ar.loc[ :, dates_col_name_ar].unique() ][::-1] ][0]) #get dates as str unique of current df
time_stamp_dates


# In[210]:


#generate dates list to match aperturas with rejected panels per cause per date
#dates_ar = [str(j).split(" ")[0].replace("/","-") if "/" in str(j).split(" ")[0] else str(j).split(" ")[0] for j in time_stamp_dates]  # dates for convert each time stamp to str and remove hh:mm:ss
#dates_ar = [ i.split("-")[::-1][0]+"-"+i.split("-")[::-1][1]+"-"+i.split("-")[::-1][2] if "2024" not in i[0:4] else i for i in dates_ar ] #truncate day and month to match date format of rejected per cause per day
#dates_ar =sorted(dates_ar) #sorted dates aperturas ascending
dates_ar =sorted(time_stamp_dates) #sorted dates aperturas ascending
dates_ar


# # Check matches on initial hour & final hour
# * remove apertures that are duplicate for changes on dat shift

# In[212]:


list_dropped_idx_rows=[]
for date_ar in dates_ar:
    print(date_ar)
    df_seeker=df_ar.loc[df_ar["Fecha Paro"]==date_ar] #filter by date
    rows_df_seeker=df_seeker.index #get idx of df for current date
    last_row=rows_df_seeker[-1] #to avoid out of range
    print(last_row)
    for row in rows_df_seeker:
        print(row)
        if row==last_row:
            continue #jump to next date
        if df_seeker.at[row,"Hora Final"]==df_seeker.at[row+1,"Hora Inicial"]:
            list_dropped_idx_rows.append(row+1) #add idx to be dropped
    print("idxs to drop are {}".format(list_dropped_idx_rows))
df_ar.drop(list_dropped_idx_rows,inplace=True) #drop selected rows for current date
df_ar


# In[213]:


amt_apertura_nariz=df_ar.groupby(dates_col_name_ar).count().T.iloc[0] #for each production stop there is an apertura de nariz and take those values
amt_apertura_nariz=np.array(amt_apertura_nariz) #agsin amt of aperturas per day on array of numpy
amt_apertura_nariz


# In[214]:


data_pointer="causa_rechazos" #start with df with rejected panels number per day and cause
df=dict_data_pointer[data_pointer] #mask causa_rechazos with df alias
dates_col_name="Fecha" #date col on causa_rechazos
cause_col_name="Notas movimiento" #rejected causes col name
nan_causes="causa no especifica" #str to replace nans on rejected causes col name
df.loc[:,[cause_col_name]]=df.loc[:,[cause_col_name]].fillna(value=nan_causes) #particular cleasing for causa_rechazos df; fill not specified rejected causes
df.loc[:,[cause_col_name]]


# ### New approach:
# * Drop date col on causa rechazos and replace w/ str date col
# * Convert str to datetime to make call correctly

# In[216]:


df.loc[:,dates_col_name]=df.loc[:,dates_col_name].astype('str').apply(lambda x: x.split(" ")[0]) #remove hh:mm:ss from date
try: #attemp to drop cummulative total row
    df=df.loc[1:,:] #drop first row cause is a total row
except:
    pass
df.reindex(range(len(df)))
df[dates_col_name]


# In[217]:


ignored_articles=["de","s","-"] #+#articles to remove for cause name-->make basic cause labelling


# In[218]:


def remove_specific_chars(string=None):
    new_cause_basic_name=string
    nan_causes="causa no especifica" #str to replace nans on rejected causes col name
    ignored_articles=["de","s","-"] #+#articles to remove for cause name-->make basic cause labelling
    ignored_digits=[str(number) for number in range(9+1)] #list to remove numbers from string
    for ignored_article in ignored_articles:
        if string==nan_causes: #do not remove chars on nan_causes
            continue
        new_cause_basic_name=new_cause_basic_name.replace(ignored_article,"") #remove articles from cause name
        new_cause_basic_name=" ".join(new_cause_basic_name.split()) #remove spaces
        new_cause_basic_name="".join([i for i in new_cause_basic_name if not i.isdigit()])
        print(new_cause_basic_name)
    return new_cause_basic_name


# In[219]:


causes=[str(i).lower() for i in df[cause_col_name].unique()] #day causes on lower case
for idx_cause,cause in enumerate(causes): #run through causes and idx from 0-len(causes)
    causes[idx_cause]=remove_specific_chars(string=cause) #" ".join(new_cause_basic_name.split()) #clean str for extra spaces
causes=list(set(causes)) #get unique instances of causes (not duplicates on causes), sorted alpha descending
time_stamp_dates=list([ i for i in [ df.loc[ :, dates_col_name].unique() ][::-1] ][0]) #get dates as time_stamps
#dates = [str(j).split(" ")[0] for j in time_stamp_dates]  # dates to convert each time stamp to str and remove hh:mm:ss info
dates=sorted(time_stamp_dates) #sorted dates aperturas ascending
causes=sorted(causes)
dates,causes


# ### Unique ID color for every cause

# In[221]:


colors_id_path=Path.joinpath(directory,"valid_causes_rejected_panels.txt")
causes_colors_df = pd.read_csv(colors_id_path, sep=",",index_col=0,header=0,on_bad_lines='skip')
causes_colors_df["variations"]=causes_colors_df["variations"].apply(lambda x:x.replace(";",","))
causes_colors_df


# # In case rejected causes is empty:
# * generate dummy causes, all current valid causes from df of valid causes

# In[223]:


if len(causes)<1: #causes list is empty
    causes=[eval(element)[0] for element in list(causes_colors_df.loc[:,list(causes_colors_df.columns)[0]].values)]
causes


# ## Dates check
# * for now, aperturas de nariz file contains dates that are missing on causa rechazos file

# In[225]:


while dates_ar!=dates and eval(input()): # [:len(dates)]
    for date_ar_idx,date_ar in enumerate( dates_ar ): #run through dates of aperturas
        print(date_ar_idx)
        print("current date of apertures ",date_ar)
        print("current dates of causas rechazos ",dates)
        if date_ar not in dates: #replace current dates with dates of aperturas de nariz: non missing dates current file
            print("{} of apertures not in {}".format(date_ar,dates))
            dates.insert(date_ar_idx,date_ar)
            print("nueva lista de fechas para causa rechazos ",dates)
dates==dates_ar


# # Generate data to plotting

# In[227]:


weight_counts={i:[0]*len(causes) for i in dates} #make dict to store panel per cause per day
weight_counts


# # TODO
# * apply directive to clean classifications and search correctly on causa rechazos

# In[229]:


name_of_rejected_panels_col="Salidas (inv.)" #actual name of rejected panels col-->start completion of panel per cause per day
for date in dates: #run through dates
    try: #------->try to search by respective date. except: date not in cause rechazos, generate a date entry on weight counts with all causes on 0<-----------
        print(date, type(date))
        print(date_col,cause_col_name)
        df_cols_date_search=df.loc[:,:"Notas movimiento"].groupby([date_col,cause_col_name]).sum().T.loc[:,date] #total amt of panels per cause, per date
    except: #ValueError:
        #print(ValueError)
        continue #next iteration, current date with all 0s on causes
    cols_date_search_causes=df_cols_date_search.columns #causes col names for current date filter
    for cause,z in zip(causes,range(len(causes))): # run through causes and idx from 0-len(causes)
        for current_date_cause in cols_date_search_causes: # # run through causes per day
            current_cause=current_date_cause.lower() #apply lower case convertion
            current_cause=remove_specific_chars(string=current_cause) #cause on current df, remove articles to basic cause name
            if cause in current_cause: #cause match case: if cause in current cause per day, 
                panels_per_cause=df_cols_date_search[current_date_cause].T[name_of_rejected_panels_col] #get panels rejected by current cause
                print(f"{cause}:"+str(panels_per_cause)) #print cause and panels
                weight_counts[date][z]=panels_per_cause #store on dict date:
    #print(date)
weight_counts


# In[230]:


construc_data_to_stacked=list(weight_counts.items()) #get keys and values of weight_counts
array_rejected_panels_per_cause_per_day=np.zeros((len(causes),len(dates))) #make array of zeros to replace data from rows as cols
for i in range(len(construc_data_to_stacked)): # run through idx from 0-len(amt of dates)
    array_rejected_panels_per_cause_per_day[:,i]=np.array(construc_data_to_stacked[i][-1]).T #take panels values, transpose and store on array of rejected panels
weight_count_causes={i:array_rejected_panels_per_cause_per_day[j,:] for i,j in zip(causes, range(len(causes)))} #reconstruct weight counts: keys as causes, rows rejected panels per specific cause per day
weight_count_causes


# In[231]:


bar_cause_labels=[[]]*len(causes) #make labels to display on rectangle bar data: inside rectangle to do not display 0 values
for bar_values,bar_idx,cause in zip(bar_cause_labels,range(len(causes)),causes): #run through bbar_cause_labels and idx from 0-len(causes) and causes
    bar_values=[str(int(weight_count_causes[cause][i])).replace("0"," ") if len( str(int(weight_count_causes[cause][i])) )<2 else str(int(weight_count_causes[cause][i])) for i in range(len(dates)) ] #replace 0 only values with " " #
    bar_cause_labels[bar_idx]=bar_values #agsin rectangle value
bar_cause_labels


# # TODO
# * organizar orden de stacked bar para mostrar primero las causas con más paneles rechazados

# In[233]:


colors_available=mcolors.TABLEAU_COLORS
colors_available


# In[234]:


colors_available_keys=list(colors_available)
#colors_available_keys.remove('tab:olive')
colors_available_keys


# In[235]:


causes_color_idxs=[]
for j in range(len(causes)):
    for i in range(len(causes_colors_df)):
        if causes[j] in causes_colors_df["variations"][i]:
            causes_color_idxs.append(int(eval(causes_colors_df.at[i,"color"])))
causes_color_idxs


# In[236]:


colors_choosen={cause:colors_available_keys[idx_color] for cause,idx_color in zip(causes,causes_color_idxs)}
colors_choosen


# In[237]:


fontsz=12 #define font size of plot components
matplotlib.rcParams.update({'font.size': fontsz}) #update font size for plot components of matplotlib


# In[238]:


fig, ax = plt.subplots()
fig.tight_layout()  # Adjust layout to prevent clipping of labels
#fig.set_figheight(8)
#fig.set_size_inches(50, 40) #set plot size
#plot aperturas
amt_dates=len(dates)
bottom = np.zeros(amt_dates) #initial axis for stacked bars plotting
plt.grid() #make grid mesh
max_bottom=0 #to store max of bottoms in construction of bar
for (data_label,weight_count),bar_value_stick,color_cause in zip(weight_count_causes.items(),bar_cause_labels,colors_choosen.values()): #run through dates, rejected per cause per dates, labels of values of rejected per cause per day 
    p = ax.bar(dates, weight_count, label=data_label, bottom=bottom,color=color_cause) #take bar plot elements: rectangle(attribute 1, attribute 2, ...)
    bottom += weight_count #make new start to plot next top rectangle
    check_bottom=np.max(bottom)
    if check_bottom>max_bottom:
        max_bottom=check_bottom #to generate ylim of causas rechazos
    ax.bar_label(p, labels=bar_value_stick, label_type='center',color="black",padding=0) #add bar height str value on bar center
leq=ax.legend(loc="best") #generate legend box for bar plot
# Get the bounding box of the original legend
bb = leq.get_bbox_to_anchor().transformed(ax.transAxes.inverted()) 
# Change to location of the legend. 
xOffset = -1.2
bb.x0 += xOffset
bb.x1 += xOffset*(1.05)
leq.set_bbox_to_anchor(bb, transform = ax.transAxes)
amt_xticks=range(len(dates))
ax.set_xticks(amt_xticks)
ax.set_xticklabels(dates,rotation=90) #rotate x axis labels 90º to be displayed vertically
ax.set_xlabel(dates_col_name) #name of bar plot x axis
rejected_panels_values=np.array(list(weight_counts.values()))
max_y_axis=np.max(rejected_panels_values) #get max of all data
ax.set_yticks(np.arange(0, max_y_axis+max_bottom, 2)) #set y axis label values: axis pitch=10 unds
ax.set_ylabel("Cantidad de rechazos [-]") #y axis name for bar plot
ax.set_aspect('auto')
#plot aperturas
ax_ar = ax.twiny() #copy bar plot element to plot easily amt of aperturas de nariz
ax_ar.sharex(ax)
amt_xticks_ar=range(len(dates))
ax_ar.set_xticks(amt_xticks_ar)
ax_ar.set_xticklabels(dates_ar,rotation=90) #rotate x axis labels 90º to be displayed vertically
ax_ar.set_xlabel(dates_col_name_ar) #name of bar plot x axis
ax_ar.plot(amt_apertura_nariz,label="Aperturas de nariz",linewidth=fontsz/5,linestyle='dashed',color="b",marker=".",
        markersize=fontsz/2,markerfacecolor='red') #plot aperturas de nariz by day
ax_ar.set_xticklabels(dates_ar,rotation=90)
leq_ar=ax_ar.legend(loc="upper right") #move legend box of aperturas to left to not cover bar plot legend box #bbox_to_anchor=(0.7, 1),
# Get the bounding box of the original legend
bb_ar = leq_ar.get_bbox_to_anchor().transformed(ax.transAxes.inverted()) 
# Change to location of the legend. 
xOffset = 0.6
bb_ar.x0 += xOffset
bb_ar.x1 += xOffset*(1.05)
leq_ar.set_bbox_to_anchor(bb_ar, transform = ax.transAxes)
secax_y2 = ax_ar.secondary_yaxis("right", functions=(lambda x: x, lambda x: x)) #make new y axis for aperturas
secax_y2.set_ylabel("Aperturas de nairz [-]",color='b') #change color of y axis to blue
max_aperturas=np.max(amt_apertura_nariz) #to set max lim of aperturas y axis
secax_y2.set_yticks(np.arange(0, max_aperturas*(1.4), 2)) #change y axis limits and pitch to 5
ax_ar.set_aspect('auto')
imgs_folder="/imgs_reports_daily" #str with name to save plots
imgs_type_folder="/qty_rejecteds_apertures"
imgs_year_folder=f"/year_{dates[0].split("-")[0]}"
imgs_month_folder=f"/month_{dates[0].split("-")[1]}"
img_name="/fail_modes_Qty_rechazos" #name of img file
str_today=datetime.today().strftime('%Y-%m-%d') #asign date of generation
plt.title("Causas y Número de Rechazos por día/ Aperturas de nariz por día") #make title
directory_to_save = Path(str(directory)+imgs_folder+imgs_type_folder+imgs_year_folder+imgs_month_folder) # get directory to save plot
directory_to_save.mkdir(exist_ok=True)
plt.savefig(str(directory_to_save)+img_name+dates[0]+"_"+dates_ar[-1]+"_"+str_today+".png", bbox_inches='tight') #store img plot
plt.show()


# In[239]:


df_to_export=pd.concat([df, df_ar], axis=1) #merge dfs to store data as old queries


# In[240]:


df_to_export.to_excel(str(directory)+f"/old_queries/{data_pointer}_{data_pointer_ar}_"+dates[0]+"_"+dates_ar[-1]+".xlsx") #save current query to old_queries


# # Plot with sorted stacked bars
# * make innner outter index data frame, sort by inner index (causes)

# In[242]:


"""times=[]
for i in dates:
    for j in range(len(causes)):
        times.append(i)
times_causes_array=[times,causes*len(dates)]
times_causes_array"""


# In[243]:


"""data=np.array(list(weight_count_causes.values())).T.flatten()
data.shape"""


# In[244]:


"""s=pd.Series(data, index=times_causes_array)"""


# In[245]:


"""s1=s.groupby(level=[0]).apply(lambda x:x.groupby(level=[1]).sum().sort_values(ascending=True))
s1"""


# In[246]:


"""s1.unstack().plot.bar(stacked=True)"""


# In[247]:


"""data,idxs=weight_count_causes.values(),weight_count_causes.keys()

data=pd.DataFrame(index=idxs,data=data,columns=dates).T
data.plot.bar()"""


# # Export notebook to make .py script

# In[288]:


get_ipython().system('jupyter nbconvert --to script bar_plot_rejected_per_cause_per_day_aperturas_nariz_per_day.ipynb')

