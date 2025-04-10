import React from 'react';
import '../style-date.css'
import '../style.css'

const StartDatePicker = ({ value, onChange }) => {
  return (
    <div className="card">
      <h3>🗓️ Дата начала 3-месячного периода</h3>
      <input
        type="date"
        value={value}
        onChange={e => onChange(e.target.value)}
        className="input-date"
      />
    </div>
  );
};

export default StartDatePicker;
