import { useQuery } from '@tanstack/react-query'
import { getFraudByType } from '../api'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

function FraudByTypeChart() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['fraudByType'],
    queryFn: getFraudByType
  })

  if (isLoading) return <div>Loading chart...</div>
  if (isError) return <div>Error loading chart</div>

  return (
    <div style={{ marginBottom: '24px' }}>
      <h2>Fraud Rate by Transaction Type</h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="type" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="total" fill="#8884d8" name="Total Transactions" />
          <Bar dataKey="fraud_count" fill="#ff4444" name="Fraud Cases" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

export default FraudByTypeChart