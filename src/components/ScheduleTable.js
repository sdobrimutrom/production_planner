
import React from 'react';
import { format, parseISO, startOfWeek, endOfWeek } from 'date-fns';
import ru from 'date-fns/locale/ru';

const ScheduleTable = ({ data }) => {
  if (!data) return null;

  const schedule = data['график'];

  // Группируем все задачи по неделям
  const weeks = {};

  Object.entries(schedule).forEach(([brigade, entries]) => {
    entries.forEach(entry => {
      const dateObj = parseISO(entry.date);
      const weekStart = format(startOfWeek(dateObj, { weekStartsOn: 1 }), 'yyyy-MM-dd');
      const weekEnd = format(endOfWeek(dateObj, { weekStartsOn: 1 }), 'yyyy-MM-dd');
      const key = `${weekStart} – ${weekEnd}`;

      if (!weeks[key]) weeks[key] = [];
      weeks[key].push({
        brigade,
        date: entry.date,
        product: entry.product,
        hours: entry.hours
      });
    });
  });

  return (
    <div style={{ marginTop: '2em' }}>
      <h3>📋 График по неделям</h3>
      {Object.entries(weeks).map(([week, rows]) => (
        <div key={week} style={{ marginBottom: '2em', border: '1px solid #ddd', padding: '1em', borderRadius: '6px' }}>
          <h4 style={{ marginBottom: '0.5em' }}>📅 Неделя: {week}</h4>
          <table style={{ borderCollapse: 'collapse', width: '100%', fontSize: '14px' }}>
            <thead>
              <tr style={{ backgroundColor: '#f0f0f0' }}>
                <th style={cellStyle}>Дата</th>
                <th style={cellStyle}>Бригада</th>
                <th style={cellStyle}>Задача</th>
                <th style={cellStyle}>Часы</th>
              </tr>
            </thead>
            <tbody>
              {rows.sort((a, b) => a.date.localeCompare(b.date)).map((row, i) => (
                <tr key={i} style={{ backgroundColor: i % 2 === 0 ? '#fff' : '#f9f9f9' }}>
                  <td style={cellStyle}>{row.date}</td>
                  <td style={cellStyle}>{row.brigade}</td>
                  <td style={cellStyle}>{row.product}</td>
                  <td style={cellStyle}>{row.hours}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}
    </div>
  );
};

const cellStyle = {
  border: '1px solid #ccc',
  padding: '6px',
  textAlign: 'center'
};

export default ScheduleTable;
