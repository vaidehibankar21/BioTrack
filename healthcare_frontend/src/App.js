import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [vitals, setVitals] = useState({
    hr: 0,
    spo2: 0,
    status: 'Connecting...',
    patient: 'Kritisha Oberoi'
  });
  const [reports, setReports] = useState([]);

  // ✅ Backend URL (UPDATED)
  const BASE_URL = "https://biotrack-zrpl.onrender.com";

  const fetchData = async () => {
    try {
      const vRes = await axios.get(`${BASE_URL}/api/vitals`);
      console.log("Vitals from Backend:", vRes.data);
      setVitals(vRes.data);

      const rRes = await axios.get(`${BASE_URL}/api/list-reports`);
      setReports(rRes.data);
    } catch (err) {
      console.error("Backend unreachable");
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, []);

  const cardStyle = {
    marginTop: '30px',
    border: `2px solid ${vitals.status === 'Normal' ? '#4caf50' : '#61dafb'}`,
    borderRadius: '15px',
    padding: '25px',
    display: 'inline-block',
    backgroundColor: '#282c34'
  };

  return (
    <div className="App" style={{
      backgroundColor: '#1a1d23',
      color: 'white',
      minHeight: '100vh',
      padding: '20px',
      fontFamily: 'Arial'
    }}>
      <h1>BioTrack Live Dashboard</h1>
      <hr style={{ borderColor: '#444' }} />

      <div style={cardStyle}>
        <h2>Patient: {vitals.patient}</h2>

        <p style={{ color: '#aaa', fontSize: '18px', marginTop: '-10px' }}>
          🕒 Last Sync:
          <span style={{ color: '#61dafb' }}>
            {vitals.time || " Fetching..."}
          </span>
        </p>

        <div style={{ fontSize: '28px', margin: '20px 0' }}>
          <p>
            Heart Rate:
            <span style={{ color: '#ff4d4d', fontWeight: 'bold' }}>
              {vitals.hr} BPM
            </span>
          </p>

          <p>
            SpO2 Levels:
            <span style={{ color: '#4caf50', fontWeight: 'bold' }}>
              {vitals.spo2}%
            </span>
          </p>
        </div>

        <h3 style={{ marginBottom: '20px' }}>
          Status:
          <span style={{
            color: vitals.status === 'Healthy' ? '#4caf50' : '#ffcc00'
          }}>
            {vitals.status}
          </span>
        </h3>

        <button
          onClick={() => window.open(`${BASE_URL}/api/download-latest`)}
          style={{
            padding: '12px 24px',
            backgroundColor: '#61dafb',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            fontWeight: 'bold'
          }}
        >
          📥 Download Latest Report
        </button>
      </div>

      <div style={{
        marginTop: '50px',
        maxWidth: '600px',
        margin: '50px auto',
        textAlign: 'left'
      }}>
        <h2>📜 Previous Reports</h2>

        {reports.length === 0 ? (
          <p>No reports yet. (Complete 10 readings to generate a report)</p>
        ) : (
          reports.map((r, i) => (
            <div key={i} style={{
              backgroundColor: '#282c34',
              padding: '15px',
              marginBottom: '10px',
              borderRadius: '8px',
              display: 'flex',
              justifyContent: 'space-between',
              border: '1px solid #444'
            }}>
              <span>{r}</span>

              <button
                onClick={() => window.open(`${BASE_URL}/api/download-report/${r}`)}
                style={{
                  background: 'none',
                  border: '1px solid #61dafb',
                  color: '#61dafb',
                  padding: '5px 10px',
                  borderRadius: '5px',
                  cursor: 'pointer'
                }}
              >
                View
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default App;