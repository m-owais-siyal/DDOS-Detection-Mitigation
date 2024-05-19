import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [command, setCommand] = useState('');

  const handleService = async (service, action) => {
    try {
      const response = await axios.get(`http://localhost:5100/${action}_${service}`);
      alert(`Response from ${action} ${service}: ${JSON.stringify(response.data)}`);
    } catch (error) {
      alert(`Error ${action} ${service}: ${error.message}`);
    }
  };

  const handleSendCommand = async () => {
    try {
      const response = await axios.post('http://localhost:5100/run_command', { command });
      alert(`Response from sending command: ${JSON.stringify(response.data)}`);
    } catch (error) {
      alert(`Error sending command: ${error.message}`);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Service Control Dashboard</h1>

        <div className="button-container">
          <button onClick={() => handleService('ryu', 'start')}>Start Ryu Controller</button>
          <button onClick={() => handleService('ryu', 'kill')}>Stop Ryu Controller</button>
        </div>

        <div className="button-container">
          <button onClick={() => handleService('mininet', 'start')}>Start Mininet</button>
          <button onClick={() => handleService('mininet', 'kill')}>Stop Mininet</button>
        </div>

        <div className="button-container">
          <button onClick={() => handleService('flask', 'start')}>Start Flask Server</button>
          <button onClick={() => handleService('flask', 'kill')}>Stop Flask Server</button>
        </div>

        <div className="button-container">
          <button onClick={() => handleService('react', 'start')}>Start React App</button>
          <button onClick={() => handleService('react', 'kill')}>Stop React App</button>
        </div>

        <div className="button-container">
          <input type="text" value={command} onChange={e => setCommand(e.target.value)} placeholder="Send command to Mininet" />
          <button onClick={handleSendCommand}>Send Command</button>
        </div>
      </header>
    </div>
  );
}

export default App;