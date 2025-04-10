
import React from 'react';
import '../style.css';

const ResultView = ({ data }) => {
  if (!data) return null;

  const { по_бригадам, загрузка, по_производству } = data;

  return (
    <div style={{ marginTop: '2em' }}>
      <h3>📆 Задачи по бригадам</h3>
      {Object.entries(по_бригадам).map(([brigade, tasks]) => (
        <div key={brigade} style={{ marginBottom: '1em' }}>
          <strong>{brigade}</strong>
          <table className="excel-table">
            <thead>
              <tr>
                <th>Изделие</th>
                <th>Тип</th>
                <th>Объем (шт)</th>
                <th>Часы</th>
              </tr>
            </thead>
            <tbody>
              {tasks.map((task, i) => (
                <tr key={i}>
                  <td>{task.product}</td>
                  <td>{task.тип}</td>
                  <td>{task.объем}</td>
                  <td>{task.часы}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}

      <h3>⏱️ Загрузка бригад</h3>
      <table className="excel-table">
        <thead>
          <tr>
            <th>Бригада</th>
            <th>Часы</th>
            <th>Лимит</th>
            <th>Загрузка (%)</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(загрузка).map(([brigade, info]) => (
            <tr key={brigade}>
              <td>{brigade}</td>
              <td>{info.часы}</td>
              <td>{info.лимит}</td>
              <td>{info["загрузка_%"]}%</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h3>📉 Выполнение плана</h3>
      <table className="excel-table">
        <thead>
          <tr>
            <th>Изделие</th>
            <th>План</th>
            <th>Факт</th>
            <th>Отклонение</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(по_производству).map(([product, res]) => (
            <tr key={product}>
              <td>{product}</td>
              <td>{res.план}</td>
              <td>{res.факт}</td>
              <td>{res.отклонение}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ResultView;
