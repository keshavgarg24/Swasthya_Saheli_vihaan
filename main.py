# Made for Swasthya Saheli
# Breast Cancer Prediction


import streamlit as st
st. set_page_config(layout="wide", page_icon=":hospital:")
st.set_option('deprecation.showPyplotGlobalUse', False)
import pandas as pd
import numpy as np
import seaborn as sns
import time
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')
plt.style.use('dark_background')

from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, LabelEncoder, StandardScaler
from sklearn.metrics import precision_recall_fscore_support as score, mean_squared_error
from sklearn.metrics import confusion_matrix,accuracy_score
from sklearn.decomposition import PCA

start_time=time.time()
tit1,tit2 = st.columns((4, 1))
tit1.markdown("<h1 style='text-align: center;'><u>Breast Cancer Prediction</u> </h1>",unsafe_allow_html=True)
st.sidebar.title("Dataset and Classifier")

dataset_name=st.header("Dataset: ",("Breast Cancer"))
classifier_name = st.sidebar.selectbox("Select Classifier: ",("Logistic Regression","KNN","SVM",
                                                              "Random Forest","Gradient Boosting"))

LE=LabelEncoder()
dataset_name="Breast Cancer"
data = pd.read_csv("original.csv")
data["diagnosis"] = LE.fit_transform(data["diagnosis"])
data.replace([np.inf, -np.inf], np.nan, inplace=True)
data["diagnosis"] = pd.to_numeric(data["diagnosis"],errors='coerce')
X = data.drop(['id','diagnosis'],axis=1)
Y = data.diagnosis

col1,col2=st.columns((1,5))
plt.figure(figsize=(12,3))
plt.title("Classes in Y")
col1.write(Y)
sns.countplot(Y, palette='gist_heat')
col2.pyplot()
st.write(data)
st.write("Shape of dataset: ",data.shape)
st.write("Number of classes: ",Y.nunique())


def add_parameter_ui(clf_name):
    params={}
    st.sidebar.write("Select values: ")

    if clf_name == "Logistic Regression":
        R = st.sidebar.slider("Regularization",0.1,10.0,step=0.1)
        MI = st.sidebar.slider("max_iter",50,400,step=50)
        params["R"] = R
        params["MI"] = MI

    elif clf_name == "KNN":
        K = st.sidebar.slider("n_neighbors",1,20)
        params["K"] = K

    elif clf_name == "SVM":
        C = st.sidebar.slider("Regularization",0.01,10.0,step=0.01)
        kernel = st.sidebar.selectbox("Kernel",("linear", "poly", "rbf", "sigmoid", "precomputed"))
        params["C"] = C
        params["kernel"] = kernel


    elif clf_name == "Random Forest":
        N = st.sidebar.slider("n_estimators",50,500,step=50,value=100)
        M = st.sidebar.slider("max_depth",2,20)
        C = st.sidebar.selectbox("Criterion",("gini","entropy"))
        params["N"] = N
        params["M"] = M
        params["C"] = C

    elif clf_name == "Gradient Boosting":
        N = st.sidebar.slider("n_estimators", 50, 500, step=50,value=100)
        LR = st.sidebar.slider("Learning Rate", 0.01, 0.5)
        L = st.sidebar.selectbox("Loss", ('deviance', 'exponential'))
        M = st.sidebar.slider("max_depth",2,20)
        params["N"] = N
        params["LR"] = LR
        params["L"] = L
        params["M"] = M

  

    RS=st.sidebar.slider("Random State",0,100)
    params["RS"] = RS
    return params

params = add_parameter_ui(classifier_name)

def get_classifier(clf_name,params):
    global clf
    if clf_name == "Logistic Regression":
        clf = LogisticRegression(C=params["R"],max_iter=params["MI"])

    elif clf_name == "KNN":
        clf = KNeighborsClassifier(n_neighbors=params["K"])

    elif clf_name == "SVM":
        clf = SVC(kernel=params["kernel"],C=params["C"])

    elif clf_name == "Random Forest":
        clf = RandomForestClassifier(n_estimators=params["N"],max_depth=params["M"],criterion=params["C"])

    elif clf_name == "Gradient Boosting":
        clf = GradientBoostingClassifier(n_estimators=params["N"],learning_rate=params["LR"],loss=params["L"],max_depth=params["M"])

    return clf

clf = get_classifier(classifier_name,params)


def model():
    X_train,X_test,Y_train,Y_test=train_test_split(X,Y,test_size=0.2,random_state=65)

    #MinMax Scaling / Normalization of data
    Std_scaler = StandardScaler()
    X_train = Std_scaler.fit_transform(X_train)
    X_test = Std_scaler.transform(X_test)

    clf.fit(X_train,Y_train)
    Y_pred = clf.predict(X_test)
    acc=accuracy_score(Y_test,Y_pred)

    return Y_pred,Y_test

Y_pred,Y_test=model()

#Plot Output
def compute(Y_pred,Y_test):
   
    pca=PCA(2)
    X_projected = pca.fit_transform(X)
    x1 = X_projected[:,0]
    x2 = X_projected[:,1]
    plt.figure(figsize=(16,8))
    plt.scatter(x1,x2,c=Y,alpha=0.8,cmap="viridis")
    plt.xlabel("Principal Component 1")
    plt.ylabel("Principal Component 2")
    plt.colorbar()
    st.pyplot()

    c1, c2 = st.columns((4,3))
    
    plt.figure(figsize=(12,6))
    plt.scatter(range(len(Y_pred)),Y_pred,color="yellow",lw=5,label="Predictions")
    plt.scatter(range(len(Y_test)),Y_test,color="red",label="Actual")
    plt.title("Prediction Values vs Real Values")
    plt.legend()
    plt.grid(True)
    c1.pyplot()

    
    cm=confusion_matrix(Y_test,Y_pred)
    class_label = ["High-risk", "Low-risk"]
    df_cm = pd.DataFrame(cm, index=class_label,columns=class_label)
    plt.figure(figsize=(12, 7.5))
    sns.heatmap(df_cm,annot=True,cmap='Pastel1',linewidths=2,fmt='d')
    plt.title("Confusion Matrix",fontsize=15)
    plt.xlabel("Predicted")
    plt.ylabel("True")
    c2.pyplot()

    acc=accuracy_score(Y_test,Y_pred)
    mse=mean_squared_error(Y_test,Y_pred)
    precision, recall, fscore, train_support = score(Y_test, Y_pred, pos_label=1, average='binary')
    st.subheader("Metrics of the model: ")
    st.text('Precision: {} \nRecall: {} \nF1-Score: {} \nAccuracy: {} %\nMean Squared Error: {}'.format(
        round(precision, 3), round(recall, 3), round(fscore,3), round((acc*100),3), round((mse),3)))

st.markdown("<hr>",unsafe_allow_html=True)
st.header(f"1) Model for Prediction of {dataset_name}")
st.subheader(f"Classifier Used: {classifier_name}")
compute(Y_pred,Y_test)


end_time=time.time()
st.info(f"Total execution time: {round((end_time - start_time),4)} seconds")


def user_inputs_ui(dataset_name,data):
    user_val = {}
    if dataset_name == "Breast Cancer":
        X = data.drop(["id","diagnosis"], axis=1)
        for col in X.columns:
            name=col
            col = st.number_input(col, abs(X[col].min()-round(X[col].std())), abs(X[col].max()+round(X[col].std())))
            user_val[name] = round((col),4)

    return user_val


st.markdown("<hr>",unsafe_allow_html=True)
st.header("2) User Values")
with st.expander("See more"):
    st.markdown("""
    In this section you can use your own values to predict the target variable. 
    Input the required values below and you will get your status based on the values. <br>
    <p style='color: red;'> 1 - High Risk </p> <p style='color: green;'> 0 - Low Risk </p>
    """,unsafe_allow_html=True)

user_val=user_inputs_ui(dataset_name,data)


def user_predict():
    global U_pred
    if dataset_name == "Breast Cancer":
        X = data.drop(["id","diagnosis"], axis=1)
        U_pred = clf.predict([[user_val[col] for col in X.columns]])

    st.subheader("Your Status: ")
    if U_pred == 0:
        st.write(U_pred[0], " - You are not at high risk :)")
    else:
        st.write(U_pred[0], " - You are at high risk :(")
user_predict()  
