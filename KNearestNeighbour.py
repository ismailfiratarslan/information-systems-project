import ProjectLibrary

# peak_time = 6.80
# energy = 85

def classification(path):
    df = ProjectLibrary.read_dataframe(path)
    ProjectLibrary.knn_classification(df)

def loadShifting(path, offer):
    __df = ProjectLibrary.read_dataframe(path)
    _df_ = ProjectLibrary.result_of_offers(__df, offer)
    ProjectLibrary.knn_classification(__df)
    ProjectLibrary.knn_classification_loadShifting(_df_)

def addHousehold(houseId, path, peak_time, energy):

    df = ProjectLibrary.read_dataframe(path)
    predicion_of_hhold = ProjectLibrary.predict_class_of_new_household(df, peak_time, energy)
    df_new_hh_added = ProjectLibrary.append_new_item_to_lists(houseId, df, predicion_of_hhold, peak_time, energy)
    ProjectLibrary.write_out_the_given_dataframe(df_new_hh_added, path)
    ProjectLibrary.knn_classification_addHousehold(df_new_hh_added)
