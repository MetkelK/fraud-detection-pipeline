import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { predict } from '../api'

function TransactionValidator() {
  const [form, setForm] = useState({
    type: 'TRANSFER',
    amount: '',
    oldbalanceOrg: '',
    newbalanceOrig: '',
    oldbalanceDest: '',
    newbalanceDest: ''
  })

  const mutation = useMutation({
    mutationFn: predict
  })

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  const handleSubmit = () => {
    mutation.mutate({
      type: form.type,
      amount: parseFloat(form.amount),
      oldbalanceOrg: parseFloat(form.oldbalanceOrg),
      newbalanceOrig: parseFloat(form.newbalanceOrig),
      oldbalanceDest: parseFloat(form.oldbalanceDest),
      newbalanceDest: parseFloat(form.newbalanceDest)
    })
  }

  const riskColor = {
    HIGH: '#ff4444',
    MEDIUM: '#ffaa00',
    LOW: '#00cc44'
  }

  return (
    <div style={{ marginBottom: '24px' }}>
      <h2>Transaction Validator</h2>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', maxWidth: '400px' }}>
        <label>
          Transaction Type
          <select name="type" value={form.type} onChange={handleChange} style={inputStyle}>
            <option>TRANSFER</option>
            <option>CASH_OUT</option>
            <option>CASH_IN</option>
            <option>PAYMENT</option>
            <option>DEBIT</option>
          </select>
        </label>
        <label>
          Amount
          <input name="amount" type="number" value={form.amount} onChange={handleChange} style={inputStyle} />
        </label>
        <label>
          Sender Balance Before
          <input name="oldbalanceOrg" type="number" value={form.oldbalanceOrg} onChange={handleChange} style={inputStyle} />
        </label>
        <label>
          Sender Balance After
          <input name="newbalanceOrig" type="number" value={form.newbalanceOrig} onChange={handleChange} style={inputStyle} />
        </label>
        <label>
          Receiver Balance Before
          <input name="oldbalanceDest" type="number" value={form.oldbalanceDest} onChange={handleChange} style={inputStyle} />
        </label>
        <label>
          Receiver Balance After
          <input name="newbalanceDest" type="number" value={form.newbalanceDest} onChange={handleChange} style={inputStyle} />
        </label>
        <button onClick={handleSubmit} style={buttonStyle}>
          {mutation.isPending ? 'Checking...' : 'Check Transaction'}
        </button>
      </div>

      {mutation.isSuccess && (
        <div style={{ marginTop: '16px', padding: '16px', borderRadius: '8px', border: `2px solid ${riskColor[mutation.data.risk_level]}` }}>
          <h3 style={{ color: riskColor[mutation.data.risk_level] }}>
            {mutation.data.risk_level} RISK
          </h3>
          <p>Fraud Probability: {(mutation.data.probability * 100).toFixed(2)}%</p>
          <p>Verdict: {mutation.data.is_fraud ? '⚠️ Likely Fraudulent' : '✅ Likely Legitimate'}</p>
        </div>
      )}

      {mutation.isError && (
        <div style={{ marginTop: '16px', color: 'red' }}>
          Error checking transaction. Please try again.
        </div>
      )}
    </div>
  )
}

const inputStyle = {
  display: 'block',
  width: '100%',
  padding: '8px',
  marginTop: '4px',
  borderRadius: '4px',
  border: '1px solid #ccc'
}

const buttonStyle = {
  padding: '10px 16px',
  backgroundColor: '#333',
  color: 'white',
  border: 'none',
  borderRadius: '4px',
  cursor: 'pointer'
}

export default TransactionValidator