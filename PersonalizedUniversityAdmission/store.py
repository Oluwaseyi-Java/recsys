

import pandas as pd
import streamlit as st
import tensorflow as tf # type: ignore
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim.models import Word2Vec



st.title('Personalized Recommender System')
d1=st.number_input('Jamb Score')
d2=st.number_input('WAEC grades')
d3=st.number_input('University Location')
d4=st.number_input('Area of Interest')
d5=st.number_input('Financial Range')

# Load dataset
data = pd.read_json('./data.json')

# Combine relevant columns into a single text feature
data['combined_features'] = data['course_description'] + ' ' + data['location'] + ' ' + data['tuition_fee'].astype(str)

# Vectorize text data using TF-IDF
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(data['combined_features']).toarray()

# Convert to TensorFlow tensors
tfidf_tensor = tf.convert_to_tensor(tfidf_matrix, dtype=tf.float32)



def get_recommendations(user_input, tfidf, data):
    # Preprocess the user input
    user_input_vector = tfidf.transform([user_input]).toarray()
    user_input_tensor = tf.convert_to_tensor(user_input_vector, dtype=tf.float32)
    
    # Calculate cosine similarity
    dot_product = tf.matmul(user_input_tensor, tfidf_tensor, transpose_b=True)
    norm_user = tf.norm(user_input_tensor, axis=1)
    norm_data = tf.norm(tfidf_tensor, axis=1)
    cosine_similarity = dot_product / (norm_user * norm_data)
    
    # Get the top N recommendations
    top_indices = tf.argsort(cosine_similarity, axis=-1, direction='DESCENDING')[:10].numpy()
    
    return data.iloc[top_indices[0]]

# Example user input
user_input = "technology innovation low tuition fee high work ethics"

# Get recommendations
recommendations = get_recommendations(user_input, tfidf, data)
print(recommendations)


data['combined_features'] = data['course_description'] + ' ' + data['location'] + ' ' + data['tuition_fee'].astype(str)
data['tokenized'] = data['combined_features'].apply(lambda x: x.split())

# Train Word2Vec model
word2vec_model = Word2Vec(sentences=data['tokenized'], vector_size=100, window=5, min_count=1, workers=4)

# Convert to TensorFlow embedding matrix
embedding_matrix = tf.constant(word2vec_model.wv.vectors) 