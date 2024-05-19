import React, { useState, useEffect } from 'react';
import { Container, Form } from 'react-bootstrap';
import axios from 'axios';
import NavBar from './NavBar';
import RealTimeChart from './RealTimeChart';
import HistoricalData from './HistoricalData';
import DataVisualization from './DataVisualization';
import AlertComponent from './AlertComponent';

function App() {
  const [selectedHeader, setSelectedHeader] = useState('');
  const [headers, setHeaders] = useState([]);

  useEffect(() => {
    const fetchHeaders = async () => {
      try {
        const response = await axios.get('http://localhost:5000/api/get_headers');
        setHeaders(response.data);
      } catch (error) {
        console.error('Failed to fetch headers:', error);
      }
    };

    fetchHeaders();
  }, []);

  return (
    <Container fluid id="home">
      <NavBar />
      <AlertComponent />
      <h2 className="component-heading">Current Network Packets:</h2>
      <RealTimeChart />
      <hr className="component-divider" />
      <h2 className="component-heading">Data Visualization:</h2>
      <Form.Control as="select" onChange={e => setSelectedHeader(e.target.value)} value={selectedHeader}>
        <option value="">Select Header for Chart</option>
        {headers.map((header) => (
          <option key={header} value={header}>{header}</option>
        ))}
      </Form.Control>
      {selectedHeader && <DataVisualization selectedHeader={selectedHeader} />}
      <hr className="component-divider" />
      <h2 className="component-heading">Historical Network Packets:</h2>
      <HistoricalData />
    </Container>
  );
}

export default App;
