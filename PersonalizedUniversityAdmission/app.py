
# From a young age, I have been deeply fascinated by problem-solving and the logic behind it. This curiosity led me to discover the world of programming, where I found great satisfaction in creating solutions through code. My passion for reading further fuels my desire to constantly learn and expand my knowledge. With a strong interest in computing and engineering, I aspire to study computer science to deepen my understanding of technology and how it can be leveraged to address complex challenges. My goal is to develop innovative solutions that can make a difference in the world.

#Core pkg
import time
import pandas as pd 
import streamlit as st
import streamlit.components.v1 as stc
import neattext.functions as nfx
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity, linear_kernel



#load dataset
#Load each course with their descriptions 
def load_course_description_data(data):
    df=pd.read_json(data)
    return df

#Load universities dataset 
def load_universities_data(data):
    df=pd.read_json(data)
    return df


#Vectorization of data & cosine similarity matrix
def vectorize_text_to_cosine_matrix(data):
    count_vector=CountVectorizer()
    cv_matrix=count_vector.fit_transform(data)
    cv_matrix.todense()
    #Get the cosine
    cosine_sim_matrix=cosine_similarity(cv_matrix)
    return cosine_sim_matrix

#Recommendation engine
def get_recommendation(description,cosine_sim_matrix,df,num_of_rec):
    #indices of the course
    course_indices = pd.Series(df.index,index=df["description"]).drop_duplicates()
    #Index of course
    idx = course_indices[description]
    #Look into the cosine matrix for that index
    sim_scores=list(enumerate(cosine_sim_matrix[idx]))
    sim_scores=sorted(sim_scores, key=lambda x: x[1], reverse=True)
    # return sim_scores[1:]
    selected_course_indices=[i[0] for i in sim_scores[1:]]
    selected_course_scores=[i[0] for i in sim_scores[1:]]

    result_df= df.iloc[selected_course_indices]
    return result_df.head(num_of_rec)
    
    #Get dataframe and title
    # result_df=df.iloc[selected_course_indices]
    # result_df["similarity_score"]= selected_course_scores
    # final_recommended_courses=result_df["name","description","similarity_score"]
    # return final_recommended_courses

#Create a set of rules to filter universities based on their location
def search_university_based_on_location(location,df):
    result_df=df[df["location"].str.contains(location)]
    return result_df
    

#Create a set of rules for University eligibility based Jamb score
# def university_jamb_score_checker(score,df):
#     federal_df=df[df["type"].str.contains("Federal")]
#     state_df=df[df["type"].str.contains("State")]
#     private_df=df[df["type"].str.contains("Private")]
    
#     if score>=220 and score<=400 :
#         return federal_df
#     elif score >=170 and score<=219:
#         return state_df
#     else: 
#         return private_df

#Create a set of rules for University eligibility baesd on School fees
# def university_school_fees_checker(school_fess,df):
#     #federal
#     federal_df=df[df["type"].str.contains("Federal")]
    
#     #state and federal
#     state_df=df[df["type"].str.contains("State")]
#     state_and_federal_df=state_df._append(federal_df)
    
#     #private, state and federal
#     private_df=df[df["type"].str.contains("Private")]
#     private_state_federal_df=private_df._append(state_and_federal_df)
 
#     #state and private
#     state_private_df=private_df._append(state_df)
    
#     if school_fess==1:
#         return federal_df
#     elif school_fess == 2:
#         return state_and_federal_df
#     elif school_fess==3:
#         return private_state_federal_df
#     else:
#         return "Select a school fees range"
    
#Create a set of rules for University eligibility based Jamb score and School fees    
def school_fees_and_jamb_score_validator(school_fees,jamb_score,df):
    #federal dataframe
    federal_df=df[df["type"].str.contains("Federal")]
    
    #state and federal dataframe
    state_df=df[df["type"].str.contains("State")]
    state_and_federal_df=state_df._append(federal_df)
    
    #private, state and federal dataframe
    private_df=df[df["type"].str.contains("Private")]
    private_state_federal_df=private_df._append(state_and_federal_df)
 
    #state and private dataframe
    state_private_df=private_df._append(state_df)
   
    if (jamb_score>=220 and jamb_score <=400) and school_fees == 3:
        return private_state_federal_df
    elif (jamb_score>=220 and jamb_score<=400) and school_fees == 2:
        return state_and_federal_df
    elif (jamb_score>=170 and jamb_score<=219) and school_fees == 3:
        return state_private_df
    elif (jamb_score >=220 and jamb_score<=400) and school_fees == 1:
        return federal_df
    elif (jamb_score >=170 and jamb_score<=219) and school_fees == 2:
        return state_df
    elif (jamb_score>=150 and jamb_score <=169) and school_fees == 3:
        return private_df
    elif (jamb_score>=170 and jamb_score<=219) and school_fees == 1:
        return ""
    elif (jamb_score>=150 and jamb_score<=169) and school_fees == 2:
        return "Likely universities that accept your Jamb score does not accept your school fees range"
    elif (jamb_score>=150 and jamb_score<=169) and school_fees == 1:
        return "Universities that accept your Jamb score does not accept your school fees range"
    else: 
        return "You do not meet the minimum requirements for admission"
        
 
def main():
    
    #Streamlit interface
    st.title('Personalized Recommender System')

    df=load_course_description_data("./custom_courses_with_descriptions.json")
    df2=load_universities_data("./updated_universities.json")
    
    Jamb_Score=st.number_input("Jamb Score")
    Subjects=st.text_input("Enter your two most proficient academic subjects (separate them with whitespace)")
    Location=st.text_input("University Location (enter the name of it's city or state)")
    Area_of_Interest=st.text_input("Area of Interest (the field you'll like to explore)")
    Hobby=st.text_input("Hobby (what you like to do most academically)")
    Financial_Range=st.selectbox("Financial Range (select 1 if you can only afford 'Below 300 Thousand Naira', select 2 if you can afford 'Below 600 Thousand Naira', select 3 if you can afford 'Above 700 Thousand Naira')", [1,2,3])
    Profile=st.text_area("Profile")
    
 
    Location=Location.capitalize()
    userProfile=Profile+Hobby+Area_of_Interest+Subjects
    newrow={
    "name":"profile", 
    "description":userProfile}
    
    df.loc[len(df)] = newrow 
    df["clean_course_description"]=df["description"].apply(nfx.remove_stopwords)
    df["clean_course_description"]=df["clean_course_description"].apply(nfx.remove_special_characters)  
    
    cosine_sim_matrix=vectorize_text_to_cosine_matrix(df["clean_course_description"])
    
    
    if st.button("Submit"):
        if Profile is not None:
            try:           
                uni_score_and_fees=school_fees_and_jamb_score_validator(Financial_Range,Jamb_Score,df2)
                uniloc=search_university_based_on_location(Location,uni_score_and_fees)
                # st.dataframe(uni_score_and_fees)
                
                st.subheader("Universities that match your preference")
                
                with st.spinner(text="In progress"):
                    time.sleep(3)
                    st.success("Done")
                for row in uniloc.iterrows():
                    uni_name=row[1][1]
                    uni_location=row[1][2]
                    uni_url=row[1][4]
                    uni_type=row[1][5]
                    
                    st.write("Name: ",uni_name)
                    st.write("Location: ",uni_location)
                    st.write("Website link: ",uni_url)
                    st.write("Type of university: ",uni_type)
                    st.divider()
                    
            except:
                st.warning("Universities that accept your Jamb score does not accept your school fees range or You do not meet the minimum requirements for admission.  \n However below are the of courses you can study based on the preferences you provided.")
                                  
            try:                    
                results=get_recommendation(userProfile,cosine_sim_matrix,df,10)
                st.subheader("Courses")
                for row in results.iterrows():
                    rec_course=row[1][0]
                    rec_description=row[1][1]
                  
                    st.write("Course: ", rec_course )
                    st.write("Description: ",rec_description)
                    st.divider()
            except:
                st.write("Not Found")
            
            
      
    

    

main()
