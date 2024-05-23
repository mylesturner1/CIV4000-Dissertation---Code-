#!/usr/bin/env python
# coding: utf-8

# ## Python Code of All Functions Used 
# 
# 1) Bearing Cap Functions
#     a) Weak Soil Base Capacity Function
#     b) Dense Soil Base Capacity Function
#     c) Skin Friction Capacity Function
#     d) Vertical Effective Stress Function
#     e) Stage 3 - Bearing Cap Function  
#     f) Stage 4 - Bearing Cap Function
# 2) Loading Data
# 3) Data Checks
# 4) Key Parameters - kN/m3
# 5) Instructions to convert file to .py file

# ## 1a) Weak Soil Base Capacity Function

# In[1]:


### Base Capacity Function Code
def weak_base_cap_calc(L, b, qc_eff):
    
    influence_zone = L + 4*b
    depth = len(qc_eff)/100
    
    if influence_zone > depth :
        Avrg_qc = float('nan')
        
    else:
        I_zone_LB = L + 4*b # Lower bound of influence zone
        I_zone_UB = L - 8*b # Upper bound of influence zone       
        
        applicable_range = [value for i, value in enumerate(qc_eff) if I_zone_UB <= (i / 100) <= I_zone_LB]
        
        Avrg_qc = sum(applicable_range) / len(applicable_range) if applicable_range else 0


    Base_cap = Avrg_qc*1000 * np.pi * b**2 * 0.25
    
    return Base_cap


# ## 1b) Dense Soil Base Capacity Function

# In[2]:


### Base Capacity Function Code
def dense_base_cap_calc(L, b, qc_eff):
    
    influence_zone = L - 2*b
    depth = len(qc_eff)/100
    
    if influence_zone > depth :
        Avrg_qc = float('nan')
        
    else:
        I_zone_LB = L  # Lower bound of influence zone
        I_zone_UB = L - 2*b # Upper bound of influence zone       
        
        applicable_range = [value for i, value in enumerate(qc_eff) if I_zone_UB <= (i / 100) <= I_zone_LB]
        
        Avrg_qc = sum(applicable_range) / len(applicable_range) if applicable_range else 0


    Base_cap = Avrg_qc*1000 * np.pi * b**2 * 0.25
    
    return Base_cap


# ## 1c) Skin Friction Capacity Function

# In[3]:


### Skin Friction Function Code 
### Note inputs only per pile
def skin_frict_calc(L, b, qc_eff):
    depth = len(qc_eff) / 100

    if L < depth:
        Skin_area = np.pi * b * (0.01)
        co_eff = 0.04 * Skin_area

        Temp_Skin_Frict = [val * co_eff * 1000 for x, val in enumerate(qc_eff) if x < L * 100]

        Skin_Frict = sum(Temp_Skin_Frict)

    else:
        Skin_Frict = float('nan')

    return Skin_Frict


# ## 1d) Vertical Effective Stress Function

# In[4]:


def eff_stress(qc, pwp):
    qc_eff = [a - b for a, b in zip(qc, pwp)] 
    qc_eff = [0 if np.isnan(x) else x for x in qc_eff]
    
    return qc_eff


# ## 1e) Stage 3 - Bearing Capacity Function

# In[5]:


def s3_spec_bear_cap(CPTu, L, b, min_cap):
    All_applic = []

    for i in range(CPTu.shape[1] // 4):
        temp_applic = []
        temp_qc = CPTu[:, i * 4 + 2]
        temp_pwp = CPTu[:, i * 4 + 3]
        temp_entries = []

        for j in range(len(L)):
            length = L[j]
            temp_qc_eff = eff_stress(temp_qc, temp_pwp)
            temp_base_cap = dense_base_cap_calc(length, b, temp_qc_eff)
            temp_skin_cap = skin_frict_calc(length, b, temp_qc_eff)
            temp_cap = temp_base_cap + temp_skin_cap

            if temp_cap >= min_cap:
                temp_entries.append([length, temp_cap])

        # Filter for the minimum length entry if there are any applicable entries
        if temp_entries:
            # Find the entry with the minimum length
            min_length_entry = min(temp_entries, key=lambda x: x[0])
            # Append the min_cap, min_length, and min_temp_cap
            temp_applic.append([min_cap, min_length_entry[0], min_length_entry[1]])
        else:
            # Append zeros when no entry meets the required bearing capacity
            temp_applic.append([0, 0, 0])

        All_applic.append(temp_applic)

    return All_applic


# ## 1f) Stage 4 - Bearing Capacity Function

# In[6]:


def s4_spec_bear_cap(CPTu, L, b, min_cap):
    All_applic = []

    for i in range(CPTu.shape[1] // 4):
        temp_applic = []
        temp_qc = CPTu[:, i * 4 + 2]
        temp_pwp = CPTu[:, i * 4 + 3]
        temp_entries = []

        for length in L:
            for diam in b:
                temp_qc_eff = eff_stress(temp_qc, temp_pwp)
                temp_base_cap = dense_base_cap_calc(length, diam, temp_qc_eff)
                temp_skin_cap = skin_frict_calc(length, diam, temp_qc_eff)
                temp_cap = temp_base_cap + temp_skin_cap
                volume = (0.25 * np.pi * diam ** 2) * length

                if temp_cap >= min_cap:
                    temp_entries.append([volume, length, diam, temp_cap])

        if temp_entries:
            min_vol_entry = min(temp_entries, key=lambda x: x[0])  # Finding minimum volume entry
            temp_applic.append(
                [min_cap, min_vol_entry[1], min_vol_entry[2], min_vol_entry[3]])  # min_cap, length, diameter, temp_cap
        else:
            temp_applic.append([0, 0, 0, 0])  # Append zeros when no entry meets the required bearing capacity

        All_applic.append(temp_applic)

    return All_applic


# ## 2a) Loading CSV Function

# In[7]:


import csv
import numpy as np

def load_csv(filename):
    data = []
    max_length = 0  # Track the maximum row length
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            # Convert each value to float if possible, keeping as is if not
            # This also handles empty strings as np.nan
            converted_row = [np.nan if value.lower() in ['nan', 'na', 'null', ''] else value for value in row]
            
            # Check if row contains np.nan values
            if np.nan in converted_row:
                continue  # Skip the row if it contains np.nan values
                
            data.append(converted_row)  # Assuming further processing will handle numeric conversion
            if len(row) > max_length:
                max_length = len(row)  # Update max_length if current row is longer
    
    return data, max_length


# ## 2b) Splitting Data Function

# In[8]:


def split_sublists(list1, list2, list3, list4):
    set1, set2, set3 = {}, {}, {}
    
    counter1, counter2, counter3 = 0, 0, 0

    div1, div2 = 3, 6  # Adjusted based on your splitting logic

    for i in range(len(list1)):
        if i < div1:
            set1[counter1] = (list1[i], list2[i], list3[i], list4[i])
            counter1 += 1
        elif i < div2:
            set2[counter2] = (list1[i], list2[i], list3[i], list4[i])
            counter2 += 1
        else:
            set3[counter3] = (list1[i], list2[i], list3[i], list4[i])
            counter3 += 1
    
    return set1, set2, set3


# ## 2c) Loading Data Function

# In[9]:


import pandas as pd

def load_csv_to_list_of_lists(filename):
    # Load the CSV file into a DataFrame
    df = pd.read_csv(filename)
    
    # Create an empty list to store the list of lists for depth measurements
    all_depths = []
    
    # Iterate over each column in the DataFrame
    for column in df.columns:
        # Use a list comprehension to exclude NaN values
        # Convert values to a list, skipping over NaNs
        all_depths.append([x for x in df[column] if pd.notna(x)])
    
    return all_depths


# ## 3) Length of set function

# In[10]:


def len_avrg(input_set):
    lengths = []
    for i in range(len(input_set)):
        lengths.append(len(input_set[i][0]))
        
    return np.mean(lengths)


# ### 4a) kN/m3 Function

# In[11]:


import numpy as np

def kN_per_m3(L, b, Bearing_cap):
    if Bearing_cap == 0:
        return 0
    else:
        volume = np.pi * (b ** 2) * 0.25 * L
        return Bearing_cap / volume


# ### 4b) Optimal Length Function

# In[12]:


def optimal_length(L, bearing_cap, Required_cap):
    if bearing_cap < Required_cap:
        Length = 0
    else:
        Length = L
        
    return Length


# ## Testing Functions

# def S2_bearing_cap(L, b, CPTu):
#
#     all_cap = []
#     for length in L:
#
#         temp_cap = []
#
#         for diam in b:
#
#             for i in range(CPTu.shape[1] // 4):
#
#                 temp_qc = CPTu[:, i * 4 + 2]
#                 temp_pwp = CPTu[:, i * 4 + 3]
#
#                 temp_qc_eff = eff_stress(temp_qc, temp_pwp)
#                 temp_base_cap = dense_base_cap_calc(length, diam, temp_qc_eff)
#                 temp_skin_cap = skin_frict_calc(length, diam, temp_qc_eff)
#
#                 calc_cap = temp_base_cap + temp_skin_cap
#
#                 temp_cap.append(calc_cap)
#
#         all_cap.append(temp_cap)
#
#     return all_cap



def replace_nans_with_last_valid(values):
    if not values:
        return values  # Return as is if the list is empty

    last_valid = None
    for i in range(len(values)):
        if math.isnan(values[i]):
            if last_valid is not None:
                values[i] = last_valid
        else:
            last_valid = values[i]
    return values


import math
import numpy as np
def S2_bearing_cap(L, b, CPTu):
    all_cap = []

    for i in range(CPTu.shape[1] // 4):
        temp_cap = []

        for diam in b:

            for length in L:
                temp_qc = CPTu[:, i * 4 + 2]
                temp_pwp = CPTu[:, i * 4 + 3]

                temp_qc_eff = eff_stress(temp_qc, temp_pwp)
                temp_base_cap = dense_base_cap_calc(length, diam, temp_qc_eff)
                temp_skin_cap = skin_frict_calc(length, diam, temp_qc_eff)

                calc_cap = temp_base_cap + temp_skin_cap
                temp_cap.append(calc_cap)

        # Apply NaN replacement to the list of calculated capacities for this length
        clean_cap = replace_nans_with_last_valid(temp_cap)
        all_cap.append(clean_cap)

    return all_cap







# This approach ensures that NaN values are replaced with the most recent valid value for the specific borehole,
# enhancing the precision and relevance of your fallback mechanism.


# This approach ensures that NaN values are replaced with the most recent valid value, even from previous length calculations.


# This adjusted version of the function will handle NaN values by replacing them with the last known valid value in the sequence of capacities.


def S1_bearing_cap(l, diam, CPTu):
    all_cap = []

    for i in range(CPTu.shape[1] // 4):

        temp_qc = CPTu[:, i * 4 + 2]
        temp_pwp = CPTu[:, i * 4 + 3]

        temp_cap = []

        for length in l:
            temp_qc_eff = eff_stress(temp_qc, temp_pwp)
            temp_base_cap = dense_base_cap_calc(length, diam, temp_qc_eff)
            temp_skin_cap = skin_frict_calc(length, diam, temp_qc_eff)

            calc_cap = temp_base_cap + temp_skin_cap

            temp_cap.append(calc_cap)

        all_cap.append(temp_cap)

    return all_cap

# In[13]:


# ## Testing function
# # Load datasets and find max row length across all sets
# train_data, train_max_length = load_csv(r"C:\Users\myles\OneDrive\Documents\University Year 4 - Sheffield\CIV4000 - Dissertation\Data\pile_data.csv")
# 
# print(training_data[0][0])
# 
# # print(training_set[0][2]) ### qcs values
# # print('')
# # print(training_set[0][3]) ### pwp values
# # print('')
# temp_qc_eff = (eff_stress(train_data[0][2], train_data[0][3]))
# 
# 
# 
# print(skin_frict_calc(5, 1, temp_qc_eff))
# print(base_cap_calc(5,1,temp_qc_eff))


# ## 5) Code to convert file to .py - add to base terminal on anaconda prompt

# cd C:\Users\myles\OneDrive\Documents\University Year 4 - Sheffield\CIV4000 - Dissertation\Data
# 
# ## Must double click this section
# jupyter nbconvert --to script Functions_CPTu_Cap_Copy.ipynb
# 
# # to reset terminal back to normal
# cd C:\Users\myles
# 
# ## Additionally ensure that the function code is run within juupyter before comverting 
# 
