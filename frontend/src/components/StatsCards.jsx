import { useQuery } from '@tanstack/react-query'
import { getStats } from '../api'

function StatsCards() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['stats'],
    queryFn: getStats
  })

  if (isLoading) return <div>Loading stats...</div>
  if (isError) return <div>Error loading stats</div>

  return (
    <div style={{ display: 'flex', gap: '16px', marginBottom: '24px' }}>
      <div style={cardStyle}>
        <h3>Total Transactions</h3>
        <p>{data.total_transactions.toLocaleString()}</p>
      </div>
      <div style={cardStyle}>
        <h3>Fraud Cases</h3>
        <p>{data.fraud_count.toLocaleString()}</p>
      </div>
      <div style={cardStyle}>
        <h3>Fraud Rate</h3>
        <p>{data.fraud_rate}%</p>
      </div>
      <div style={cardStyle}>
        <h3>Total Fraud Amount</h3>
        <p>${data.total_fraud_amount.toLocaleString()}</p>
      </div>
    </div>
  )
}

const cardStyle = {
  flex: 1,
  padding: '16px',
  border: '1px solid #ccc',
  borderRadius: '8px',
  textAlign: 'center'
}

export default StatsCards