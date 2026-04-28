import React from 'react';
import './App.css';
import MapComponent from './components/MapComponent';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Deprem Haritası</h1>
      </header>
      <main>
        <MapComponent />
      </main>
    </div>
  );
}

export default App;
