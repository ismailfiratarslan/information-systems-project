import pandas as pd
import datetime
import matplotlib.pyplot as plt
from sklearn import preprocessing
from sklearn import neighbors, datasets
import numpy as np
from matplotlib.colors import ListedColormap
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import os.path
import pathlib


def get_specific_time_interval(household, start_date, end_date, df):
    """
    It takes an input dataframe and extracts the data with specific household and specific time.
    """
    df_day = df[df["LCLid"] == household]
    df_day_mask = df_day[df_day.day.between(start_date, end_date)]

    return df_day_mask


def countHouseNumber(df: pd.DataFrame):
    """
    It takes an input dataframe and counts the all unique household number and saves their IDs.
    This function is specific for half hourly datasets
    """

    print("Counting starts...")
    HouseIds = []
    HouseIds.append(df.loc[:0, 'LCLid'].iloc[0])
    i = 0
    while i < df.shape[0]:
        if df.loc[i, 'LCLid'] != HouseIds[-1]:
            HouseIds.append(df.loc[i, 'LCLid'])
        i += 17280

    print("Length : ", len(HouseIds))
    return len(HouseIds), HouseIds


def convert_to_be_with_day_feature(_df: pd.DataFrame):
    """
    It takes an input dataframe and extracts the same data
    with additional two columns which are the 'day' and 'clock'.
    The columns refers only the date(Ex : 2021-03-12) and only the clock(Ex : 04:40:10) time in order.

    """

    _df['day'] = _df.tstp.str[:10]
    _df['clock'] = _df.tstp.str[11:19]
    _df.drop('tstp', inplace=True, axis=1)
    return _df


def write_out_the_given_dataframe(df_, out_path):
    """
    It takes an input dataframe and write out the given path
    """

    df_.to_csv(out_path, index=False,
               header=True, float_format='%.4f')


def read_dataframe(data_path):
    """
    It takes a csv file path to read and return the dataframe
    """

    df_ = pd.read_csv(data_path, header=0)
    return df_


def collect_and_detect_max_load_clock(df: pd.DataFrame):
    """
    It takes a dataframe which should include hourly info of one day ,
    and detects the maximum energy consumed time as a peak load.
    """
    max_value = 0
    index_ = 0
    for i in df.index.values:
        if float(df.loc[i, 'energy(kWh/hh)']) > max_value:
            max_value = float(df.loc[i, 'energy(kWh/hh)'])
            index_ = i

    return df.loc[index_, 'clock']


def take_max_load_time_of_days(household_, df_: pd.DataFrame, start_date_, end_date_):
    """
    It takes a dataframe, a household ID and two different date.
    It returns the most used peak time of a month for the specific household and time interval
    """
    _start_date = datetime.datetime.strptime(start_date_, "%Y-%m-%d")
    _end_date = datetime.datetime.strptime(end_date_, "%Y-%m-%d")
    days = (_end_date - _start_date).days
    max_load_times = []

    for i in range(days):
        print("  %", round((i / days) * 100), '..', end="\r")
        cur_day = _start_date + datetime.timedelta(days=i + 1)
        cur_day_str = cur_day.strftime("%Y-%m-%d")
        day_data = get_specific_time_interval(
            household=household_, start_date=cur_day_str, end_date=cur_day_str, df=df_)
        max_load_time = collect_and_detect_max_load_clock(day_data)
        max_load_times.append(max_load_time)

    # print("Max loadt times: ",max_load_times)

    load_dict = {}
    for i in max_load_times:
        try:
            load_dict[i] += 1
        except:
            load_dict[i] = 1

    return sorted(load_dict, key=load_dict.__getitem__, reverse=True)[0]


def get_consumed_energy_of_day(df_, hID, _date):
    """
    It returns the daily consumed energy of a household
    """
    __df = df_[(df_['LCLid'] == hID) & (df_['day'] == _date)]
    e_sum = __df['energy_sum'].iloc[0]
    return e_sum


def get_average_consumed_energy_of_days(df, hID, __start_date, __end_date):
    """
    It returns the mean of daily consumed energies of a month for specific household
    """
    __df = df[df['LCLid'] == hID]
    __df = __df[__df.day.between(__start_date, __end_date)]
    # print(type(__df[['energy_sum']].mean()))
    return __df[['energy_sum']].mean().iloc[0]


def get_average_consumed_energy_of_days_knn(df, hID, __start_date, __end_date):
    """
    It returns the mean of daily consumed energies of a month for specific household
    """
    __df = df[df['LCLid'] == hID]
    __df = __df[__df.day.between(__start_date, __end_date)]
    # print(type(__df[['energy_sum']].mean()))
    return __df[['energy(kWh/hh)']].mean().iloc[0]


def transform_datetime_to_decimal(dTimeStr):
    hour_ = int(dTimeStr[:2])
    half_ = int(dTimeStr[3:5])
    if half_ > 0:
        hour_ = hour_ + 1 / 2
    return hour_


def plot_labeled_data(transformed_data, labels_):
    """
       It plots the labeled data with 5 classes
       """
    for i in range(len(transformed_data)):
        if labels_[i] == 1:
            plt.plot(transformed_data[i][0], transformed_data[i][1], 'bo')
        elif labels_[i] == 0:
            plt.plot(transformed_data[i][0], transformed_data[i][1], 'ro')
        elif labels_[i] == 2:
            plt.plot(transformed_data[i][0], transformed_data[i][1], 'mo')
        elif labels_[i] == 3:
            plt.plot(transformed_data[i][0], transformed_data[i][1], 'yo')

        else:
            plt.plot(transformed_data[i][0], transformed_data[i][1], 'co')

    plt.xlabel('Peak Load Time')
    plt.ylabel('Total consumed Energy (kW)')
    plt.title("Plot Before new household added")

    plt.show()


def predict_class_of_new_household(df, peak_time, energy):
    """
    This function takes input transformed data list and label list which come from Kmeans.py as output.
    And also takes average monthly energy of a house and peak time of household and makes a predicition about the class of new added household.
    It returns the predicted class of a household
    X data
    y class
    """
    # df1 = pd.DataFrame(label_list,
    #                    columns=['label'])
    #
    # df2 = pd.DataFrame(transformed_data_list,
    #                    columns=['peak_hour', 'average_energy'])
    #
    # df_result = pd.concat([df2, df1], axis=1, join='inner')
    X = df.iloc[:, [1, 2]].values
    y = df.iloc[:, 3].values
    print(X)
    print(y)
    h = .02

    n_neighbors = 6
    clf = neighbors.KNeighborsClassifier(n_neighbors, weights='distance')
    clf.fit(X, y)

    dataClass = clf.predict([[peak_time, energy]])

    if dataClass == 0:
        print('Prediction: ', dataClass)
        return 0
    elif dataClass == 1:
        print('Prediction: ', dataClass)
        return 1
    elif dataClass == 2:
        print('Prediction: ', dataClass)
        return 2
    elif dataClass == 3:
        print('Prediction: ', dataClass)
        return 3

    else:
        print('Prediction: ', dataClass)
        return 4


def append_new_item_to_lists(houseId, df, prediction_of_hhold, peak_time, energy):
    """
       It appends the peak time and energy of new added household to the new list.
       It is made for K-NearestNeighbour.py
       It returns the 2 lists
       """
    dict = {'ID': houseId, 'peak_hour': peak_time, 'average_energy': energy, 'Class': prediction_of_hhold}

    df = df.append(dict, ignore_index=True)

    return df

def result_of_offers(df: pd.DataFrame, offer, number_of_classes=6):
    _df_ = None
    initialized_=False
    for i in range(5):
        _df = df.loc[df['Class']==i]
        change =2 # indicates the hour that the houses will change their peak_hour as much as this number

        number_of_rows = _df.shape[0] # The number of household the class has

        if offer == "30%":
            accepted_household_percentage = round((3/10) * number_of_rows)
        elif offer == "40%":
            accepted_household_percentage = round((4/10) * number_of_rows)
        elif offer == "50%":
            accepted_household_percentage = round((5/10) * number_of_rows)
        elif offer == "60%":
            accepted_household_percentage = round((6/10) * number_of_rows)
        elif offer == "70%":
            accepted_household_percentage = round((7/10) * number_of_rows) # 

        if _df['peak_hour'].mean() >= 15: # If the peak hour average of a class is after 15.00 o'clock then change will be neagative
            change=-2 

        top_df = _df.iloc[:accepted_household_percentage] # First %40 ?(can change) percentage of a class
       
        top_df['peak_hour']+=change # Changing the peak hours
        bottom_df= _df.iloc[accepted_household_percentage:] # Not accepted houses in a class

        if not initialized_: # This condition is used just to initialize a dataFrame
            _df_ = top_df
            initialized_=True
        else:
            _df_ = pd.concat([_df_,top_df]) # Concatenate the updated data
        # print("##")
        _df_ = pd.concat([_df_,bottom_df])  # Concatenate the rest of unaccepted households data
        # print(top_df)
    # print("=>> ",_df_)
    # print("###$$#$$#$#$#$")
    
    return _df_

def knn_classification(df: pd.DataFrame):
    """
       This function makes the KNN classification
       """
    n_neighbors = 6
    X = df.iloc[:, [1, 2]].values
    y = df.iloc[:, 3].values
    h = .02

    cmap_light = ListedColormap(['#FFAAAA', '#AAFFAA', '#00AAFF', "#ad40ff", "#ffff00","#00FF00","#800000"])
    cmap_bold = ListedColormap(['#FF0000', '#0000FF', '#FF00FF', "#FFFF00", "#00FFFF","#00FF00","#800000"])

    clf = neighbors.KNeighborsClassifier(n_neighbors, weights='distance')
    clf.fit(X, y)

    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                         np.arange(y_min, y_max, h))

    Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])

    Z = Z.reshape(xx.shape)
    # plt.figure()

    plt.scatter(X[:, 0], X[:, 1], c=y, cmap=cmap_bold)

    plt.title("K-Nearest Neighbour Classification (number of neighbours = %i)" % (n_neighbors))
    plt.xlabel('Peak Load Time')
    plt.ylabel('Total consumed Energy (kW)')
    plt.savefig('figure_images/saved_figure_classification.png', dpi = 150)
    plt.savefig('figure_images/saved_figure_beforeloadShifting.png', dpi = 85)
    plt.clf()
    # plt.show()

def knn_classification_addHousehold(df: pd.DataFrame):
    """
       This function makes the KNN classification
       """
    n_neighbors = 6
    X = df.iloc[:, [1, 2]].values
    y = df.iloc[:, 3].values
    h = .02

    cmap_light = ListedColormap(['#FFAAAA', '#AAFFAA', '#00AAFF', "#ad40ff", "#ffff00","#00FF00","#800000"])
    cmap_bold = ListedColormap(['#FF0000', '#0000FF', '#FF00FF', "#FFFF00", "#00FFFF","#00FF00","#800000"])

    clf = neighbors.KNeighborsClassifier(n_neighbors, weights='distance')
    clf.fit(X, y)

    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                         np.arange(y_min, y_max, h))

    Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])

    Z = Z.reshape(xx.shape)
    # plt.figure()

    plt.scatter(X[:, 0], X[:, 1], c=y, cmap=cmap_bold)

    plt.title("After Adding New Household")
    plt.xlabel('Peak Load Time')
    plt.ylabel('Total consumed Energy (kW)')
    plt.savefig('figure_images/saved_figure_addHousehold.png', dpi = 150)
    # plt.show()

def knn_classification_loadShifting(df: pd.DataFrame):
    """
       This function makes the KNN classification
       """
    n_neighbors = 6
    X = df.iloc[:, [1, 2]].values
    y = df.iloc[:, 3].values
    h = .02

    cmap_light = ListedColormap(['#FFAAAA', '#AAFFAA', '#00AAFF', "#ad40ff", "#ffff00","#00FF00","#800000"])
    cmap_bold = ListedColormap(['#FF0000', '#0000FF', '#FF00FF', "#FFFF00", "#00FFFF","#00FF00","#800000"])

    clf = neighbors.KNeighborsClassifier(n_neighbors, weights='distance')
    clf.fit(X, y)

    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                         np.arange(y_min, y_max, h))

    Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])

    Z = Z.reshape(xx.shape)
    # plt.figure()

    plt.scatter(X[:, 0], X[:, 1], c=y, cmap=cmap_bold)

    plt.title("After Load Shifting")
    plt.xlabel('Peak Load Time')
    plt.ylabel('Total consumed Energy (kW)')
    plt.savefig('figure_images/saved_figure_afterloadShifting.png', dpi = 85)
    plt.clf()
    # plt.show()

def kmeans_clustering(df_daily_path, df_hh_path, df_output_path, df_processed_path, start_date_daily, end_date_daily):
    df__daily = read_dataframe(df_daily_path)

    cur_path = pathlib.Path(__file__).parent.resolve()

    if os.path.isfile(df_output_path) is False:
        df_hourly_to_be_coverted = read_dataframe(df_hh_path)
        converted_df_hourly = convert_to_be_with_day_feature(
            df_hourly_to_be_coverted)
        write_out_the_given_dataframe(converted_df_hourly, df_output_path)

    _df_ = read_dataframe(df_processed_path)

    LenOfHouseIds, HouseIds = countHouseNumber(_df_)

    transformed_data = []
    cc = 0
    for i in HouseIds[:50]:
        cc += 1
        try:
            t_time = take_max_load_time_of_days(
                i, _df_, start_date_daily, end_date_daily)
            e_sum = get_average_consumed_energy_of_days(
                df__daily, i, start_date_daily, end_date_daily)
            # print(cc, ' Max load time of ', i, " is ", t_time,
            # " and avrg consumed energy is:", e_sum)
            time_t = transform_datetime_to_decimal(t_time)
            transformed_data.append([time_t, round(e_sum, 2)])
        except:
            # print(cc, ' The data does not exist for ', i,
            #       " between given interval ", start_date_daily, " : ", end_date_daily)
            HouseIds.remove(i)

    print("Transformed Data : ", transformed_data)
    # transformed_data = shuffle(transformed_data)
    print("Shuffled Transformed Data : ", transformed_data)

    points = []
    clabels = []

    print("123...")

    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(transformed_data)

    kmeans = KMeans(
        init="random",
        n_clusters=5,
        n_init=100,
        max_iter=1000,
        random_state=42
    )

    kmeans.fit(transformed_data)

    # The lowest SSE value
    # print(kmeans.inertia_)

    # Final locations of the centroid
    # print(kmeans.cluster_centers_)

    # The number of iterations required to converge
    # print(kmeans.n_iter_)
    # print(kmeans.labels_)

    # for i in range(len(transformed_data)):
    #     if kmeans.labels_[i] == 1:
    #         plt.plot(transformed_data[i][0], transformed_data[i][1], 'bo')
    #     elif kmeans.labels_[i] == 0:
    #         plt.plot(transformed_data[i][0], transformed_data[i][1], 'ro')
    #     elif kmeans.labels_[i] == 2:
    #         plt.plot(transformed_data[i][0], transformed_data[i][1], 'co')
    #     elif kmeans.labels_[i] == 3:
    #         plt.plot(transformed_data[i][0], transformed_data[i][1], 'mo')
    #
    #     else:
    #         plt.plot(transformed_data[i][0], transformed_data[i][1], 'yo')
    #
    # plt.xlabel('Peak Load Time')
    # plt.ylabel('Total consumed Energy (kW)')
    #
    # plt.show()
    return transformed_data, HouseIds, kmeans.labels_


def merge_df_for_knn(df_daily_path, df_hf_hourly_path, df_output_path,
                     df_processed_path, start_date_daily, end_date_daily):
    data, houseids, labels = kmeans_clustering(df_daily_path, df_hf_hourly_path, df_output_path,
                                               df_processed_path, start_date_daily, end_date_daily)

    df = pd.DataFrame(houseids,
                      columns=['ID'])

    df1 = pd.DataFrame(labels,
                       columns=['Class'])

    df2 = pd.DataFrame(data,
                       columns=['peak_hour', 'average_energy'])

    df_result = pd.concat([df, df2, df1], axis=1, join='inner')

    return df_result