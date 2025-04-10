import React, { useState } from 'react';
import BrigadesForm from './components/BrigadesForm';
import ProductsForm from './components/ProductsForm';
import StartDatePicker from './components/StartDatePicker';
import ScheduleTable from './components/ScheduleTable';
import ResultView from './components/ResultView';
import axios from 'axios';
import './style.css';

function App() {
  const [brigades, setBrigades] = useState([]);
  const [products, setProducts] = useState([]);
  const [startDate, setStartDate] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleCalculate = async () => {
    if (!startDate) {
      alert('Пожалуйста, выберите дату начала расчета');
      return;
    }

    try {
      const response = await axios.post('http://localhost:5000/optimize', {
        brigades,
        products,
        startDate
      });
      setResult(response.data);
      setError('');
    } catch (err) {
      setError(err?.response?.data?.error || 'Произошла ошибка при расчете');
    }
  };

  return (
    <div className="container">
      <h2>🛠️ Планировщик загрузки бригад</h2>
      <StartDatePicker value={startDate} onChange={setStartDate} />
      <BrigadesForm onChange={setBrigades} />
      <ProductsForm brigades={brigades} onChange={setProducts} />
      <div style={{ margin: '1em 0' }}>
        <button onClick={handleCalculate} className="btn">📊 Рассчитать график</button>
      </div>
      {error && <div className="error">{error}</div>}
      {result && <>
        <ResultView data={result} />
        <ScheduleTable data={result} />
      </>}
    </div>
  );
}

export default App;
