
import React from 'react';
import '../style.css';

const AlphaInput = ({ value, onChange }) => {
  return (
    <div className="card">
      <h3>⚖️ Настройка коэффициента α</h3>
      <label htmlFor="alpha">
        Вес равномерной загрузки (α):
        <input
          id="alpha"
          type="number"
          step="0.01"
          min="0.01"
          max="10"
          value={value}
          onChange={(e) => onChange(parseFloat(e.target.value))}
          className="input-number"
        />
      </label>
      <div style={{ marginTop: '0.5em', fontSize: '14px', color: '#555' }}>
        <ul style={{ paddingLeft: '1.2em' }}>
          <li>α &lt; 1 — приоритет на выполнение плана</li>
          <li>α = 1 — сбалансировано</li>
          <li>α &gt; 1 — приоритет на равномерность</li>
        </ul>
      </div>
    </div>
  );
};

export default AlphaInput;
