import streamlit as st
import requests
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import (
    precision_score,
    recall_score,
    confusion_matrix,
    RocCurveDisplay,
    PrecisionRecallDisplay,
    ConfusionMatrixDisplay,
)
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

def main():
    # Title and description
    st.title("Binary Classification WebApp")
    st.markdown("Are your mushrooms edible or poisonous? 🍄")

    st.sidebar.title("Binary Classification")
    st.sidebar.markdown("Are your mushrooms edible or poisonous?")

    # Load dataset
    @st.cache_data(persist=True)  # Cache data loading for better performance
    def load_data():
        url = 'https://raw.githubusercontent.com/nabusboi/Mushroom/main/ML-WebApp-with-Streamlit-and-Python-master/mushrooms.csv'
        try:
            response = requests.get(url)
            response.raise_for_status()  # Check if the request was successful
            data = pd.read_csv(url)  # Load the CSV data into a DataFrame
            st.write(data.head())  # Display the first few rows of the data for debugging
            return data
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching the data: {e}")
        return None

    # Preprocessing function to encode categorical columns
    def preprocess_data(df):
        # Use LabelEncoder to convert categorical columns to numeric
        le = LabelEncoder()
        for column in df.columns:
            if df[column].dtype == 'object':
                df[column] = le.fit_transform(df[column])
        return df

    # Split dataset into training and testing sets
    @st.cache_data(persist=True)
    def split_data(df):
        y = df.type
        x = df.drop(columns=['type'])
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=0)
        return x_train, x_test, y_train, y_test

    # Plot performance metrics
    def plot_metrics(metrics_list, model, x_test, y_test, class_names):
        if 'Confusion Matrix' in metrics_list:
            st.subheader("Confusion Matrix")
            cm = confusion_matrix(y_test, model.predict(x_test))
            disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)
            disp.plot()
            st.pyplot()

        if 'ROC Curve' in metrics_list:
            st.subheader("ROC Curve")
            RocCurveDisplay.from_estimator(model, x_test, y_test)
            st.pyplot()

        if 'Precision-Recall Curve' in metrics_list:
            st.subheader("Precision-Recall Curve")
            PrecisionRecallDisplay.from_estimator(model, x_test, y_test)
            st.pyplot()

    # Load and preprocess data
    df = load_data()
    if df.empty:
        return  # Stop execution if data is not available

    df = preprocess_data(df)  # Preprocess the data to convert categorical to numeric

    x_train, x_test, y_train, y_test = split_data(df)
    class_names = ['edible', 'poisonous']

    # Sidebar options for model selection
    st.sidebar.subheader("Choose Classifier")
    classifier = st.sidebar.selectbox("Classifier", ("Support Vector Machine (SVM)", "Logistic Regression", "Random Forest"))

    # SVM Classifier
    if classifier == "Support Vector Machine (SVM)":
        st.sidebar.subheader("Model Hyperparameters")
        C = st.sidebar.number_input("C (Regularization parameter)", 0.01, 10.0, step=0.01, key='C')
        kernel = st.sidebar.radio("Kernel", ("rbf", "linear"), key='kernel')
        gamma = st.sidebar.radio("Gamma (Kernel Coefficient)", ("scale", "auto"), key='gamma')

        metrics = st.sidebar.multiselect("What metrics to plot?", ('Confusion Matrix', 'ROC Curve', 'Precision-Recall Curve'))

        if st.sidebar.button("Classify", key='classify_svm'):
            st.subheader("Support Vector Machine (SVM) Results")
            model = SVC(C=C, kernel=kernel, gamma=gamma)
            model.fit(x_train.values, y_train.values)  # Ensure data is in numpy array format
            accuracy = model.score(x_test, y_test)
            y_pred = model.predict(x_test)

            # Debugging: Check shapes of y_test and y_pred
            st.write("Shape of y_test:", y_test.shape)
            st.write("Shape of y_pred:", y_pred.shape)

            # Try to compute precision score and handle potential errors
            try:
                precision = precision_score(y_test, y_pred)
                recall = recall_score(y_test, y_pred)
                st.write("Accuracy: ", round(accuracy, 2))
                st.write("Precision: ", round(precision, 2))  # Use round() instead of precision.round(2)
                st.write("Recall: ", round(recall, 2))  # Use round() instead of recall.round(2)
                plot_metrics(metrics, model, x_test, y_test, class_names)
            except ValueError as e:
                st.error(f"Error calculating precision and recall: {e}")
                st.write("Please check the data and ensure there are no mismatched or missing values.")
        
    # Logistic Regression Classifier
    if classifier == "Logistic Regression":
        st.sidebar.subheader("Model Hyperparameters")
        C = st.sidebar.number_input("C (Regularization parameter)", 0.01, 10.0, step=0.01, key='C_LR')
        max_iter = st.sidebar.slider("Maximum number of iterations", 100, 500, key='max_iter')

        metrics = st.sidebar.multiselect("What metrics to plot?", ('Confusion Matrix', 'ROC Curve', 'Precision-Recall Curve'))

        if st.sidebar.button("Classify", key='classify_lr'):
            st.subheader("Logistic Regression Results")
            model = LogisticRegression(C=C, max_iter=max_iter)
            model.fit(x_train.values, y_train.values)  # Ensure data is in numpy array format
            accuracy = model.score(x_test, y_test)
            y_pred = model.predict(x_test)

            try:
                precision = precision_score(y_test, y_pred)
                recall = recall_score(y_test, y_pred)
                st.write("Accuracy: ", round(accuracy, 2))
                st.write("Precision: ", round(precision, 2))  # Use round() instead of precision.round(2)
                st.write("Recall: ", round(recall, 2))  # Use round() instead of recall.round(2)
                plot_metrics(metrics, model, x_test, y_test, class_names)
            except ValueError as e:
                st.error(f"Error calculating precision and recall: {e}")

    # Random Forest Classifier
    if classifier == "Random Forest":
        st.sidebar.subheader("Model Hyperparameters")
        n_estimators = st.sidebar.number_input("The number of trees in the forest", 100, 5000, step=10, key='n_estimators')
        max_depth = st.sidebar.number_input("The maximum depth of the tree", 1, 20, step=1, key='max_depth')
        bootstrap = st.sidebar.radio("Bootstrap samples when building trees", ('True', 'False'), key='bootstrap')

        metrics = st.sidebar.multiselect("What metrics to plot?", ('Confusion Matrix', 'ROC Curve', 'Precision-Recall Curve'))

        if st.sidebar.button("Classify", key='classify_rf'):
            st.subheader("Random Forest Results")
            model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, bootstrap=bootstrap, n_jobs=-1)
            model.fit(x_train.values, y_train.values)  # Ensure data is in numpy array format
            accuracy = model.score(x_test, y_test)
            y_pred = model.predict(x_test)

            try:
                precision = precision_score(y_test, y_pred)
                recall = recall_score(y_test, y_pred)
                st.write("Accuracy: ", round(accuracy, 2))
                st.write("Precision: ", round(precision, 2))  # Use round() instead of precision.round(2)
                st.write("Recall: ", round(recall, 2))  # Use round() instead of recall.round(2)
                plot_metrics(metrics, model, x_test, y_test, class_names)
            except ValueError as e:
                st.error(f"Error calculating precision and recall: {e}")

    # Show raw data
    if st.sidebar.checkbox("Show raw data", False):
        st.subheader("Mushroom Data Set (Classification)")
        st.write(df)

if __name__ == '__main__':
    main()
