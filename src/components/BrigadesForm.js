import React, { useState } from 'react';
import '../style.css';

const BrigadesForm = ({ onChange }) => {
  const [brigades, setBrigades] = useState([
    { name: '', peopleCount: '', load: '' }
  ]);

  const update = (newList) => {
    setBrigades(newList);
    onChange(newList);
  };

  const handleChange = (i, key, value) => {
    const updated = [...brigades];
    updated[i][key] = value;
    update(updated);
  };

  const addBrigade = () => update([...brigades, { name: '', peopleCount: '', load: '' }]);

  const deleteBrigade = (index) => {
    const updated = brigades.filter((_, i) => i !== index);
    update(updated);
  };

  return (
    <div className="card">
      <h3>👷 Бригады</h3>
      <button onClick={addBrigade} className="btn">+ Добавить бригаду</button>
      <table className="excel-table">
        <thead>
          <tr>
            <th>Название</th>
            <th>Чел.</th>
            <th>Часы/мес</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {brigades.map((b, i) => (
            <tr key={i}>
              <td><input value={b.name} onChange={e => handleChange(i, 'name', e.target.value)} /></td>
              <td><input type="number" value={b.peopleCount} onChange={e => handleChange(i, 'peopleCount', e.target.value)} /></td>
              <td><input type="number" value={b.load} onChange={e => handleChange(i, 'load', e.target.value)} /></td>
              <td><button onClick={() => deleteBrigade(i)} className="btn btn-danger">🗑</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default BrigadesForm;
