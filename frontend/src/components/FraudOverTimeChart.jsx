import { useQuery } from '@tanstack/react-query'
import { getFraudOverTime } from '../api'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

function FraudOverTimeChart() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['fraudOverTime'],
    queryFn: getFraudOverTime
  })

  if (isLoading) return <div>Loading chart...</div>
  if (isError) return <div>Error loading chart</div>

  return (
    <div style={{ marginBottom: '24px' }}>
      <h2>Fraud Cases Over Time</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="step" label={{ value: 'Hour', position: 'insideBottom', offset: -5 }} />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="fraud_count" stroke="#ff4444" name="Fraud Cases" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export default FraudOverTimeChart