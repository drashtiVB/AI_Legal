import os.path
import streamlit as st 
import re
import sqlite3 
import pickle
import pandas as pd
import bz2

def set_bg_hack_url():
    st.markdown(
          f"""
          <style>
          .stApp {{
              background: url("https://i.ibb.co/pwVPLh9/BK.jpg");
              background-size: cover
          }}
          </style>
          """,
          unsafe_allow_html=True
      )
set_bg_hack_url()
st.title("WELCOME TO AI LEGAL TEXT")
import nltk
nltk.download('stopwords')



def remove_stopwords(text):
    stopwords=nltk.corpus.stopwords.words('english')
    clean_text=' '.join([word for word in text.split() if word not in stopwords])
    return clean_text
from nltk.stem.porter import PorterStemmer
def cleanup_data(df):
    # remove handle
    df['clean'] = df["case study"].str.replace("@", "") 
    # remove links
    df['clean'] = df['clean'].str.replace(r"http\S+", "") 
    # remove punctuations and special characters
    df['clean'] = df['clean'].str.replace("[^a-zA-Z]", " ") 
    # remove stop words
    df['clean'] = df['clean'].apply(lambda text : remove_stopwords(text.lower()))
    # split text and tokenize
    df['clean'] = df['clean'].apply(lambda x: x.split())
    # let's apply stemmer
    stemmer = PorterStemmer()
    df['clean'] = df['clean'].apply(lambda x: [stemmer.stem(i) for i in x])
    # stitch back words
    df['clean'] = df['clean'].apply(lambda x: ' '.join([w for w in x]))
    # remove small words
    df['clean'] = df['clean'].apply(lambda x: ' '.join([w for w in x.split() if len(w)>3]))

Data = st.sidebar.selectbox("Data:",['Home','Register 📰','Login ✒️'])

conn = sqlite3.connect('data.db')
c = conn.cursor()
def create_usertable():
    c.execute('CREATE TABLE IF NOT EXISTS userstable(FirstName TEXT,Mobile TEXT,Gender TEXT,Age TEXT,Email TEXT,password TEXT,Cpassword TEXT)')
def add_userdata(FirstName,Mobile,Gender,Age,Email,password,Cpassword):
    c.execute('INSERT INTO userstable(FirstName,Mobile,Gender,Age,Email,password,Cpassword) VALUES (?,?,?,?,?,?,?)',(FirstName,Mobile,Gender,Age,Email,password,Cpassword))
    conn.commit()
def login_user(Email,password):
    c.execute('SELECT * FROM userstable WHERE Email =? AND password = ?',(Email,password))
    data = c.fetchall()
    return data  
def view_all_users():
	c.execute('SELECT * FROM userstable')
	data = c.fetchall()
	return data
def delete_user(Email):
    c.execute("DELETE FROM userstable WHERE Email="+"'"+Email+"'")
    conn.commit()
    
    
     
if Data == 'Home':
    st.text("Abstract")
    st.text("AI Legal is an AI-based approach that utilizes case descriptions in order to predict law section classifications based on K-Nearest Neighbors (KNN), Linear Support Vector Machine (SVM), Decision Tree, Random Forest and Extra Trees Classifier. These models were chosen because of their advantage in dealing with large quantities of legal data and diverse feature interdependencies. In classification based on proximity, we have KNN while for the linear decision boundaries, Linear SVM is the best model. Decision Trees are easy to interpret, and Random Forest reduces variance and produces more accurate results. But Extra Trees Classifier yields the highest accuracy and training speed as well as less prone to overfitting")
                    
if Data=="Register 📰":
    Fname = st.text_input("First Name")
    Mname = st.text_input("Mobile Number")
    menu1 = ["Male","Female"]
    Ggender = st.selectbox("Gender",menu1)
    if Ggender=="Male":
        Gender=0
    else:
        Gender=1
    Aage = st.text_input("Enter your Age")
    Email = st.text_input("Email")
    Password = st.text_input("Password",type="password")
    Cpassword = st.text_input("Confirm Password",type="password")
    b2=st.button("SignUp")
    if b2:
        pattern=re.compile("(0|91)?[7-9][0-9]{9}")
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if Password==Cpassword:
            if (pattern.match(Mname)):
                if re.fullmatch(regex, Email):
                    create_usertable()
                    add_userdata(Fname,Mname,Ggender,Aage,Email,Password,Cpassword)
                    st.success("SignUp Success")
                    st.info("Go to Logic Section for Login")
                else:
                    st.warning("Not Valid Email")         
            else:
                st.warning("Not Valid Mobile Number")
        else:
            st.warning("Pass Does Not Match")
    

if Data=="Login ✒️":
    Email = st.sidebar.text_input("Email")
    Password = st.sidebar.text_input("Password",type="password")
    b1=st.sidebar.checkbox("Login")
    if b1:
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.fullmatch(regex, Email):
            create_usertable()
            if Email=='a@a.com' and Password=='123':
                st.success("Logged In as {}".format("Admin"))
                Email=st.text_input("Delete Email")
                if st.button('Delete'):
                    delete_user(Email)
                    user_result = view_all_users()
                    clean_db = pd.DataFrame(user_result,columns=["FirstName","LastName","Mobile","Gender","Age","Email","password","Cpassword"])
                    st.dataframe(clean_db)
            else:
                result = login_user(Email,Password)
                if result:
                    st.success("Logged In as {}".format(Email))
                    
                    names = ["K-Nearest Neighbors", "Liner SVM",
                             "Decision Tree", "Random Forest",
                             "ExtraTreesClassifier"]
                    classifier=st.selectbox("Select ML",names)                  
                    texts=str(st.text_input("Enter Case Study"))
                    import pandas as pd
                    df=pd.DataFrame({"case study":[texts]})
                    if st.button('Predict Section'):
                        def word_count(text):
                            return len(text.split())
                        words = word_count(texts)
                        if words > 10 and  words<=100:
                            sfile1 = bz2.BZ2File('All Model', 'r')
                            models=pickle.load(sfile1)
                            sfile2 = bz2.BZ2File('All Vector', 'r')
                            vectorizer=pickle.load(sfile2)
                            cleanup_data(df)
                            feature=vectorizer.transform([df["clean"][0]])
                            if classifier==names[0]:
                                st.success("The Section is "+str(models[0].predict(feature)[0]))
                            if classifier==names[1]:
                                st.success("The Section is "+str(models[1].predict(feature)[0]))
                            if classifier==names[2]:
                                st.success("The Section is "+str(models[2].predict(feature)[0]))
                            if classifier==names[3]:
                                st.success("The Section is "+str(models[3].predict(feature)[0]))
                            if classifier==names[4]:
                                st.success("The Section is "+str(models[4].predict(feature)[0]))
                            
                        else:
                           st.error("Word not Match in range 10 to 100 words")
                            
                else:
                    st.warning("Incorrect Email/Password")
        else:
            st.warning("Not Valid Email")
