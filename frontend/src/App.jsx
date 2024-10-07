import React, { useState, useEffect } from "react";
import axios from "axios";

const App = () => {
  const [predictedSign, setPredictedSign] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Function to fetch prediction from the Flask backend
  const fetchPrediction = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await axios.get("http://127.0.0.1:8080/");
      setPredictedSign(response.data.prediction);
    } catch (err) {
      setError("Failed to load prediction");
    }
    setLoading(false);
  };

  // Poll the backend for prediction every 2 seconds
  useEffect(() => {
    const intervalId = setInterval(() => {
      fetchPrediction();
    }, 2000); // 2000ms = 2s

    return () => clearInterval(intervalId); // Cleanup on component unmount
  }, []);

  return (
    <div style={styles.container}>
      <h1>Sign Language Translator</h1>

      <div style={styles.videoContainer}>
        <h3>Live Camera Feed:</h3>
        {/* Use <video> tag for live video feed from backend */}
        <img
          src="http://127.0.0.1:8080/"
          alt="Live Video Feed"
          style={styles.video}
        />
      </div>

      <div style={styles.prediction}>
        <h3>Prediction:</h3>
        {loading ? (
          <p>Loading...</p>
        ) : error ? (
          <p style={styles.error}>{error}</p>
        ) : (
          <h2>{predictedSign || "No sign detected yet"}</h2>
        )}
      </div>
    </div>
  );
};

// Basic styles for layout
const styles = {
  container: {
    textAlign: "center",
    padding: "20px",
  },
  videoContainer: {
    margin: "20px 0",
  },
  video: {
    width: "640px",
    height: "480px",
    border: "2px solid #ccc",
  },
  prediction: {
    marginTop: "20px",
  },
  error: {
    color: "red",
  },
};

export default App;
