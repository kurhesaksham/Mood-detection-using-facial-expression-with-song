# 🎶 Mood Detection Using Facial Expressions with Songs  

## 📌 Project Description  
An AI-based application that detects a user’s mood from facial expressions and plays songs that match the detected emotion. Using **computer vision** and **machine learning**, the system captures real-time webcam input, classifies emotions such as *Happy, Sad, Angry, Neutral, and Surprise*, and recommends or plays songs accordingly. The goal is to provide an interactive and personalized music experience by connecting human emotions with music.  

---

## 🚀 Features  
- 🎭 Real-time **facial emotion detection**  
- 🎶 Automatic **song recommendation** based on mood  
- 📷 **Webcam-based live input**  
- 🌐 Fetch songs from **YouTube** or local storage  
- 📊 Simple **Streamlit interface**  

---

## 🛠️ Tech Stack  
- **Language**: Python  
- **Libraries**: OpenCV,TensorFlow,FER,Streamlit,numpy,
- **Database**: Firebase 

---

## 📂 Project Structure  
mood_music_app/
│
├── app.py                    
├── requirements.txt
│
├── auth/
│   ├── db.py                   
│   ├── login.py               
│   ├── signup.py              
│   └── _init_.py
│
├── model/
│   └── mood_detector.py      
│
├── youtube/
│   └── youtube_player.py      
│
└── data/
    └── mood_model.h5          
