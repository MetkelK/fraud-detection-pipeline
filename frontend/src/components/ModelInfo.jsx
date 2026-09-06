import { useQuery } from '@tanstack/react-query'
import { getModelInfo } from '../api'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

function ModelInfo() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['modelInfo'],
    queryFn: getModelInfo
  })

  if (isLoading) return <div>Loading model info...</div>
  if (isError) return <div>Error loading model info</div>

  const featureData = Object.entries(data.feature_importances).map(([name, value]) => ({
    name,
    importance: parseFloat(value.toFixed(4))
  })).sort((a, b) => b.importance - a.importance)

  return (
    <div style={{ marginBottom: '24px' }}>
      <h2>Model Performance</h2>
      <div style={{ display: 'flex', gap: '16px', marginBottom: '16px' }}>
        <div style={cardStyle}>
          <h3>Best AUC</h3>
          <p>{data.auc}</p>
        </div>
        <div style={cardStyle}>
          <h3>Test AUC</h3>
          <p>{data.test_auc}</p>
        </div>
        <div style={cardStyle}>
          <h3>Trees</h3>
          <p>{data.best_params.numTrees}</p>
        </div>
        <div style={cardStyle}>
          <h3>Max Depth</h3>
          <p>{data.best_params.maxDepth}</p>
        </div>
      </div>
      <h3>Feature Importances</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={featureData} layout="vertical">
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" domain={[0, 0.4]} />
          <YAxis type="category" dataKey="name" width={120} />
          <Tooltip />
          <Bar dataKey="importance" fill="#8884d8" name="Importance" />
        </BarChart>
      </ResponsiveContainer>
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

export default ModelInfo