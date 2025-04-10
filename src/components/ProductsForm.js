import React, { useState } from 'react';
import '../style.css';

const ProductsForm = ({ brigades, onChange }) => {
  const [products, setProducts] = useState([
    { name: '', serialPlan: '', nonSerialPlan: '', assemblyRate: '', productionRates: {}, qualifications: {} }
  ]);

  const update = (newList) => {
    setProducts(newList);
    onChange(newList);
  };

  const handleChange = (i, key, value) => {
    const updated = [...products];
    updated[i][key] = value;
    update(updated);
  };

  const handleNested = (i, key, subKey, value) => {
    const updated = [...products];
    updated[i][key][subKey] = value;
    update(updated);
  };

  const addProduct = () => update([...products, {
    name: '', serialPlan: '', nonSerialPlan: '', assemblyRate: '',
    productionRates: {}, qualifications: {}
  }]);

  const deleteProduct = (index) => {
    const updated = products.filter((_, i) => i !== index);
    update(updated);
  };

  return (
    <div className="card">
      <h3>📦 Изделия</h3>
      <button onClick={addProduct} className="btn">+ Добавить изделие</button>
      <table className="excel-table">
        <thead>
          <tr>
            <th>Название</th>
            <th>Серийный план</th>
            <th>Н/серийный план</th>
            <th>Слесарка (шт/ч)</th>
            {brigades.map((b, i) => (
              <th key={i} colSpan="2">{b.name}</th>
            ))}
            <th></th>
          </tr>
          <tr>
            <td colSpan="4"></td>
            {brigades.map((_, i) => (
              <>
                <td key={`r${i}`}>шт/ч</td>
                <td key={`q${i}`}>Квал.</td>
              </>
            ))}
            <td></td>
          </tr>
        </thead>
        <tbody>
          {products.map((p, i) => (
            <tr key={i}>
              <td><input value={p.name} onChange={e => handleChange(i, 'name', e.target.value)} /></td>
              <td><input type="number" value={p.serialPlan} onChange={e => handleChange(i, 'serialPlan', e.target.value)} /></td>
              <td><input type="number" value={p.nonSerialPlan} onChange={e => handleChange(i, 'nonSerialPlan', e.target.value)} /></td>
              <td><input type="number" value={p.assemblyRate} onChange={e => handleChange(i, 'assemblyRate', e.target.value)} /></td>
              {brigades.map((b, j) => (
                <>
                  <td key={`rate-${j}`}>
                    <input type="number" value={p.productionRates[b.name] || ''} onChange={e => handleNested(i, 'productionRates', b.name, e.target.value)} />
                  </td>
                  <td key={`qual-${j}`}>
                    <input type="number" value={p.qualifications[b.name] || ''} onChange={e => handleNested(i, 'qualifications', b.name, e.target.value)} />
                  </td>
                </>
              ))}
              <td><button onClick={() => deleteProduct(i)} className="btn btn-danger">🗑</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ProductsForm;
